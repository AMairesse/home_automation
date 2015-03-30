"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.utils.timezone import utc
from heat_control.models import Sensor, Heater, Ruleset, Rule, Temperature
from datetime import datetime, timedelta
from decimal import *

class HeaterHysteresisTestCase(TestCase):
    def setUp(self):
        Ruleset.objects.create(id= "1", name= "Test_ruleset1", type= "Minimal")
        ruleset = Ruleset.objects.get(name="Test_ruleset1")
        Rule.objects.create(id= "1", ruleset= ruleset, weekday= "1", time= "00:00:00", temp= 20)
        Heater.objects.create(  id= "1",
                                hostname= "test",
                                name= "Test_heater1",
                                address= "ABCD",
                                type= "ZigBee",
                                controller = "HY",
                                freq= 120,
                                status = True,
                                gpio= 1,
                                mode= "Low",
                                description= "Test",
                                hysteresis= 1
                                )
        heater = Heater.objects.get(name="Test_heater1")
        Sensor.objects.create(  id= "1",
                                hostname= "test",
                                name= "Test_sensor1",
                                address= "ABCD",
                                type= "ZigBee",
                                freq= 600,
                                status = True,
                                gpio= 1,
                                offset= "-1.000",
                                room_name= "Test",
                                ruleset= ruleset,
                                heater= heater
                                )

    def test_offset(self):
        heater = Heater.objects.get(name="Test_heater1")
        sensor = Sensor.objects.get(name="Test_sensor1")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 10)
        Temperature.objects.create(sensor= sensor, date= date, temp= 10)
        self.assertEqual(sensor.get_last_temperature()['temp'], 9)

    def test_heater_on(self):
        heater = Heater.objects.get(name="Test_heater1")
        sensor = Sensor.objects.get(name="Test_sensor1")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 5)
        # offset is set to -1 so real temperature will be 19 which should activate the heater
        Temperature.objects.create(sensor= sensor, date= date, temp= Decimal(19.9))
        self.assertEqual(heater.get_heater_state(), True)

    def test_heater_off(self):
        heater = Heater.objects.get(name="Test_heater1")
        sensor = Sensor.objects.get(name="Test_sensor1")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 3)
        # offset is set to -1 so real temperature will be 20 which should stop the heater
        Temperature.objects.create(sensor= sensor, date= date, temp= Decimal(21))
        self.assertEqual(heater.get_heater_state(), False)

class HeaterProportionalTestCase(TestCase):
    def setUp(self):
        Ruleset.objects.create(id= "2", name= "Test_ruleset2", type= "Minimal")
        ruleset = Ruleset.objects.get(name="Test_ruleset2")
        Rule.objects.create(id= "2", ruleset= ruleset, weekday= "1", time= "00:00:00", temp= 20)
        Heater.objects.create(  id= "2",
                                hostname= "test",
                                name= "Test_heater2",
                                address= "ABCD",
                                type= "ZigBee",
                                controller = "PI",
                                freq= 120,
                                status = True,
                                gpio= 1,
                                mode= "Low",
                                description= "Test",
                                hysteresis= 1
                                )
        heater = Heater.objects.get(name="Test_heater2")
        Sensor.objects.create(  id= "2",
                                hostname= "test",
                                name= "Test_sensor2",
                                address= "ABCD",
                                type= "ZigBee",
                                freq= 600,
                                status = True,
                                gpio= 1,
                                offset= "0.000",
                                room_name= "Test",
                                ruleset= ruleset,
                                heater= heater
                                )

    def test_get_last_temperature_from_date(self):
        heater = Heater.objects.get(name="Test_heater2")
        sensor = Sensor.objects.get(name="Test_sensor2")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 30)
        temp = Temperature.objects.create(sensor= sensor, date= date, temp= 18)
        self.assertEqual(sensor.get_last_temperature_from_date(now)['temp'], 18)

    def test_heater_I_ratio_full(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.I_ratio(Decimal(17.5), 20), 1)

    def test_heater_I_ratio_half(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.I_ratio(Decimal(18.75), 20), 0.5)

    def test_heater_I_ratio_off(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.I_ratio(20, 20), 0)

    def test_heater_P_ratio_full(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.P_ratio(19, 20), 1)

    def test_heater_P_ratio_half(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.P_ratio(Decimal(19.5), 20), 0.5)

    def test_heater_P_ratio_off(self):
        heater = Heater.objects.get(name="Test_heater2")
        self.assertEqual(heater.P_ratio(20, 20), 0)

    def test_heater_on(self):
        heater = Heater.objects.get(name="Test_heater2")
        sensor = Sensor.objects.get(name="Test_sensor2")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 30)
        Temperature.objects.create(sensor= sensor, date= date, temp= Decimal(18))
        self.assertEqual(heater.get_heater_state(), True)

    def test_heater_off(self):
        heater = Heater.objects.get(name="Test_heater2")
        sensor = Sensor.objects.get(name="Test_sensor2")
        now = datetime.now().replace(tzinfo=utc)
        date = now - timedelta(minutes = 30)
        Temperature.objects.create(sensor= sensor, date= date, temp= Decimal(21))
        self.assertEqual(heater.get_heater_state(), False)

