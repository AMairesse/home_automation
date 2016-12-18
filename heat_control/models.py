from django.db import models
from django.db.models import Avg
from datetime import datetime, timedelta
from django.utils.timezone import utc
from decimal import *

SENSOR_TYPE = (('W1', 'W1'), ('ZigBee', 'ZigBee'), ('enOcean', 'enOcean'))
HEATER_TYPE = (('GPIO', 'GPIO'), ('ZigBee', 'ZigBee'))
HEATER_CONTROLLER = (('HY', 'Hysteresis'), ('PI', 'Proportional-Integral'))
RULESET_TYPE = (('Minimal', 'Minimal temperature'), ('Maximal', 'Maximal temperature'))
MODE = (('Low', 'Active low'), ('High', 'Active High'))
ISOWEEKDAY = {1: 'monday', 2: 'tuesday', 3: 'wednesday', 4: 'thursday', 5: 'friday', 6: 'saturday', 7: 'sunday'}


class Ruleset(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=RULESET_TYPE)

    def get_active_rule(self):
        today = datetime.now()
        # Get active rule for today
        rule = None
        for i in range(7):
            day = today - timedelta(days=i)
            day_of_week = day.isoweekday()
            try:
                rule = Rule.objects.all().filter(ruleset=self).filter(weekday=day_of_week).\
                                          filter(time__lte=day.time()).latest('time')
            except:
                # If no rule found then try again
                continue
            break
        return rule

    def __unicode__(self):
        return self.name + ' (' + self.type + ')'


class Rule(models.Model):
    ruleset = models.ForeignKey(Ruleset, related_name='rules')
    weekday = models.PositiveSmallIntegerField()
    time = models.TimeField()
    temp = models.DecimalField(max_digits=3, decimal_places=1)

    def get_weekday_str(self):
        return ISOWEEKDAY[self.weekday]

    def __unicode__(self):
        return 'Starting ' + self.get_weekday_str() + ' at ' + str(self.time) +\
               ' temperature is set to : ' + str(self.temp) + 'C'


class Heater(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=10, choices=HEATER_TYPE)
    controller = models.CharField(max_length=3, choices=HEATER_CONTROLLER, default='HY')
    freq = models.PositiveIntegerField()
    status = models.BooleanField()
    gpio = models.PositiveSmallIntegerField(null=True, blank=True)
    mode = models.CharField(max_length=4, choices=MODE, default='Low')
    description = models.CharField(max_length=50, null=True, blank=True)
    hysteresis = models.DecimalField(max_digits=3, decimal_places=1, default=0.2)

    def get_previous_state(self):
        try:
            previous_state = Heater_history.objects.all().filter(heater=self).latest('date').state
        except:
            previous_state = False
        return previous_state

    def get_heater_state(self):
        if self.controller == 'HY':
            return self.heater_state_hysteresis()
        elif self.controller == 'PI':
            return self.heater_state_PI()
        else:
            return False
    
    def heater_state_hysteresis(self):
        # For each sensor linked to this heater,
        # check the active rule against the last temperature.
        # If at least one sensor request heating then we return 'True'
        sensors = Sensor.objects.all().filter(heater=self)
        previous_state = self.get_previous_state()
        for sensor in sensors:
            active_rule = sensor.ruleset.get_active_rule()
            # If there is no active rule then this sensor is inactive
            if active_rule is None:
                continue
            if previous_state is False:
                # If heater is off we should turn it on only if 
                # temperature is below set point less hysteresis
                wanted_temp = active_rule.temp - self.hysteresis
            else:
                # If heater is on we should turn it off only if
                # temperature is above set point more hysteresis
                wanted_temp = active_rule.temp + self.hysteresis
            last_temperature = sensor.get_last_temperature()['temp']
            if last_temperature is not None:
                if last_temperature < wanted_temp:
                    return True
        return False

    def heater_state_PI(self):
        # For each sensor linked to this heater,
        # check the active rule against the last half-hour temperature.
        # If at least one sensor request heating then we return 'True'
        sensors = Sensor.objects.all().filter(heater=self)
        for sensor in sensors:
            # Calculate the integral ratio from the last half-hour
            now = datetime.now(utc)
            reference_time = now - timedelta(minutes=30)
            avg = Temperature.objects.all().filter(sensor=sensor)\
                                           .filter(date__gte=reference_time)\
                                           .filter(date__lte=now).aggregate(Avg('offseted_temp'))['offseted_temp__avg']
            # if there was no temperature in the last 30 minutes then go to the next sensor
            if avg is None:
                continue
            else:
                previous_temperature = Decimal(avg)
            active_rule = sensor.ruleset.get_active_rule()
            wanted_temp = active_rule.temp
            I_ratio = self.I_ratio(previous_temperature, wanted_temp)

            # Adding a proportional ratio from current mesure
            actual_temperature = sensor.get_last_temperature()['temp']
            P_ratio = self.P_ratio(actual_temperature, wanted_temp)

            # Get the needed working time
            needed_working_minutes = int(min(1, (P_ratio + I_ratio)) * 30)
            
            # Get the real working time for the last 30 minutes
            working_time_list = self.get_poweron_list(reference_time, now)
            total_time = timedelta(seconds=0)
            for [start, end] in working_time_list:
                total_time = total_time + (end - start)
                
            real_working_minutes = int(total_time.total_seconds() / 60)
            
            # If should be working if there is more than 3 mn left
            if (needed_working_minutes - real_working_minutes) > 3:
                return True
        return False

    @staticmethod
    def I_ratio(temperature, wanted_temperature):
        # For 2.5 degrees we want 100% working ratio
        # For 0 degree we want 0% working ratio
        ratio = min(1, max(0, (Decimal('0.4') * (wanted_temperature - temperature))))
        return ratio

    @staticmethod
    def P_ratio(temperature, wanted_temperature):
        # For 1 degrees we want 100% working ratio
        # For 0 degrees we want 0% working ratio
        ratio = min(1, max(0, (wanted_temperature - temperature)))
        return ratio

    def get_last_history(self):
        try:
            last_history = Heater_history.objects.all().filter(heater=self.id).latest('date')
            state = last_history.state
            date = last_history.date
        except:
            state = None
            date = None
        return {'state': state, 'date': date}

    def get_poweron_list(self, date_min, date_max):
        history = Heater_history.objects.all().filter(heater=self.id).filter(date__gte=date_min).\
            filter(date__lte=date_max)
        result = []
        previous_date = date_min
        # Build a list of tuples when the heater was on
        for temp_history in history:
            if temp_history.state is False:
                result.append([previous_date, temp_history.date])
            previous_date = temp_history.date
        # if the last element is true the we should add to the list until date_max
        # Warning : this is a query set, negative indexing is not supported
        if history.count() > 0:
            last_element = history[history.count()-1]
            if last_element.state is True:
                result.append([last_element.date, date_max])
        return result

    def __unicode__(self):
        return self.name + ' (' + self.hostname + ')'


class Heater_history(models.Model):
    heater = models.ForeignKey(Heater, related_name='history')
    date = models.DateTimeField(db_index=True)
    state = models.BooleanField()

    def __unicode__(self):
        if self.state is True:
            state_str = 'on'
        else:
            state_str = 'off'
        return 'At ' + self.date.strftime('%c') + ' ' + self.heater.name + ' was set to ' + state_str


class Sensor(models.Model):
    hostname = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50, null=True, blank=True)
    type = models.CharField(max_length=10, choices=SENSOR_TYPE)
    freq = models.PositiveIntegerField()
    status = models.BooleanField()
    gpio = models.PositiveSmallIntegerField(null=True, blank=True)
    rorg = models.PositiveSmallIntegerField(null=True, blank=True)
    rorg_func = models.PositiveSmallIntegerField(null=True, blank=True)
    rorg_type = models.PositiveSmallIntegerField(null=True, blank=True)
    offset = models.DecimalField(max_digits=4, decimal_places=3, blank=True, default=0.0)
    room_name = models.CharField(max_length=50)
    ruleset = models.ForeignKey(Ruleset, related_name='sensors', null=True, blank=True)
    heater = models.ForeignKey(Heater, related_name='sensors', null=True, blank=True)

    def get_last_temperature(self):
        try:
            last_temperature = Temperature.objects.all().filter(sensor=self.id).latest('date')
            temp = last_temperature.offseted_temp
            date = last_temperature.date
        except:
            temp = None
            date = None
        return {'temp': temp, 'date': date}

    def get_last_temperature_from_date(self, maxtime):
        try:
            last_temperature = Temperature.objects.all().filter(sensor=self.id).filter(date__lte=maxtime).latest('date')
            temp = last_temperature.offseted_temp
            date = last_temperature.date
        except:
            temp = None
            date = None
        return {'temp': temp, 'date': date}

    def __unicode__(self):
        return self.room_name + ' (' + self.hostname + ' - ' + self.name + ')'


class Temperature(models.Model):
    sensor = models.ForeignKey(Sensor, related_name='temperatures')
    date = models.DateTimeField(db_index=True)
    temp = models.DecimalField(max_digits=5, decimal_places=3)
    offseted_temp = models.DecimalField(max_digits=5, decimal_places=3, blank=True)
    
    def save(self, *args, **kwargs):
        self.offseted_temp = self.temp + self.sensor.offset
        super(Temperature, self).save(*args, **kwargs)  # Call the "real" save() method.
    
    def get_day(self):
        return self.date.strftime('%d-%m-%Y')
    
    def __unicode__(self):
        return str(self.offseted_temp) + 'C (at ' + self.date.strftime('%c') + ')'
