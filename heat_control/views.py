from django.template import Context, loader
from django.http import HttpResponse, Http404
from heat_control.models import Sensor, Temperature, Heater, Heater_history, Ruleset, Rule
from django.db.models import Avg
from datetime import datetime, timedelta
from django.utils.timezone import utc
from rest_framework import generics
from heat_control.serializers import SensorSerializer, TemperatureSerializer, HeaterSerializer, HeaterHistorySerializer, RulesetSerializer, RuleSerializer
import json

class SensorList(generics.ListCreateAPIView):
    """
    List all sensors, or create a new sensor.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class SensorDetail(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update a sensor.
    """
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer

class TemperatureRecord(generics.CreateAPIView):
    """
    Record a temperature.
    """
    queryset = Temperature.objects.all()
    serializer_class = TemperatureSerializer

class HeaterList(generics.ListCreateAPIView):
    """
    List all heaters, or create a new one.
    """
    queryset = Heater.objects.all()
    serializer_class = HeaterSerializer

class HeaterDetail(generics.RetrieveAPIView):
    """
    Retrieve a heater and calculate status from rules and each sensor last temperature.
    """
    queryset = Heater.objects.all()
    serializer_class = HeaterSerializer

class HeaterHistoryRecord(generics.CreateAPIView):
    """
    Record a heater state change.
    """
    queryset = Heater_history.objects.all()
    serializer_class = HeaterHistorySerializer

class RulesetList(generics.ListCreateAPIView):
    """
    List all rulesets, or create a new one.
    """
    queryset = Ruleset.objects.all()
    serializer_class = RulesetSerializer

class RulesetDetail(generics.RetrieveAPIView):
    """
    Retrieve a ruleset
    """
    queryset = Ruleset.objects.all()
    serializer_class = RulesetSerializer

class RuleList(generics.ListCreateAPIView):
    """
    List all rules, or create a new one.
    """
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

class RuleDetail(generics.RetrieveAPIView):
    """
    Retrieve a rule  
    """
    queryset = Rule.objects.all()
    serializer_class = RuleSerializer

def hourly_averages(sensor, date_min, date_max):
    delta = date_max - date_min
    # Note : nb_hours need a "+1" because of 23:59:59
    nb_hours = int(round(delta.seconds/3600 + delta.days*24))+1
    # Get corresponding temperatures objects
    temps = Temperature.objects.all().filter(sensor = sensor).filter(date__gte=date_min).filter(date__lte=date_max)
    result = []
    for i in range(nb_hours, 0, -1):
        # 'i' is going from 'nb_hours' to 1 included
        # so that hour_max will finally be equal to date_max
        hour_min = date_max - timedelta(hours=i)
        hour_max = date_max - timedelta(hours=i-1)
        hour_temps = [x.offseted_temp for x in temps if (x.date > hour_min) and (x.date <= hour_max)]
        if hour_temps != [] :
            avg_temp = float(sum(hour_temps)) / len(hour_temps)
            result.append(round(avg_temp, 2))
        else:
            result.append(None)
    result_json = json.dumps(result)
    return {str(sensor.room_name) : result_json}

def heater_poweron_list(heater, date_min, date_max):
    history = Heater_history.objects.all().filter(heater = heater).filter(date__gte=date_min).filter(date__lte=date_max)
    result = []
    previous_date = date_min
    # Build a list of tuples when the heater was on
    for temp_history in history:
        if (temp_history.state == False):
            result.append([previous_date, temp_history.date])
        previous_date = temp_history.date
    # if the last element is true the we should add to the list until date_max
    # Warning : this is a query set, negative indexing is not supported
    if (history[history.count()-1].state == True):
        result.append([history[-1].date, date_max])
    return result

def index(request):
    # Init template
    t = loader.get_template('heat_control/index.html')
    context_data = {}
    c = Context(context_data)
    return HttpResponse(t.render(c), content_type="text/html")

def ruleset(request):
    # Init template
    t = loader.get_template('heat_control/ruleset.html')
    context_data = {}
    # Get sensors list
    sensor_list = Sensor.objects.all().filter(status = True).order_by('-hostname')[:5]
    context_data.update({'sensor_list': sensor_list})
    # Get ruleset list
    ruleset_list = Ruleset.objects.all().order_by('-name')
    context_data.update({'ruleset_list': ruleset_list})
    # Send response
    c = Context(context_data)
    return HttpResponse(t.render(c), content_type="text/html")

def day_graph(request, year_start, month_start, day_start, year_end, month_end, day_end):
    # Init template
    t = loader.get_template('heat_control/day_graph.html')
    context_data = {}
    # Get sensors list
    sensor_list = Sensor.objects.all().filter(status = True).order_by('-hostname')[:5]
    # Get heaters list
    heater_list = Heater.objects.all().filter(status = True).order_by('-hostname')[:5]
    # Get chart data
    try:
        date_min = datetime(int(year_start), int(month_start), int(day_start), 0, 0, 0).replace(tzinfo=utc)
        date_min_str = date_min.strftime('%A %d %B %Y')
        date_max = datetime(int(year_end), int(month_end), int(day_end), 23, 59, 59).replace(tzinfo=utc)
        date_max_str = date_max.strftime('%A %d %B %Y')
        context_data.update({'date_min': date_min_str, 'date_max': date_max_str, 'year': year_start, 'month': month_start, 'day': day_start})
    except:
        raise Http404
    categories_list = []
    # Get average temperature for each sensor
    chart_series = dict()
    for sensor in sensor_list:
        hourly_avg = hourly_averages(sensor, date_min, date_max)
        chart_series.update(hourly_avg)
    context_data.update({'chart_series': chart_series})
    # Get the power on serie for each heater
    poweron_series = []
    for heater in heater_list:
        poweron_list = heater_poweron_list(heater, date_min, date_max)
        poweron_series.extend(poweron_list)
    context_data.update({'poweron_series': poweron_series})
    # Send response
    c = Context(context_data)
    return HttpResponse(t.render(c), content_type="text/html")






