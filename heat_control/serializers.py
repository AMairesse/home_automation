from heat_control.models import Sensor, Temperature, SENSOR_TYPE, HEATER_TYPE, HEATER_CONTROLLER, Heater, Heater_history, Ruleset, RULESET_TYPE, MODE, Rule
from rest_framework import serializers


class SensorSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.ChoiceField(choices=SENSOR_TYPE)
    id = serializers.HyperlinkedIdentityField(view_name='sensor-detail')
    gpio = serializers.IntegerField(required=False)
    rorg = serializers.IntegerField(required=False)
    rorg_func = serializers.IntegerField(required=False)
    rorg_type = serializers.IntegerField(required=False)
    last_temperature = serializers.SerializerMethodField('get_last_temperature')
    offset = serializers.DecimalField(required=False)
    ruleset = serializers.HyperlinkedRelatedField(view_name='ruleset-detail', required=False)
    heater = serializers.HyperlinkedRelatedField(view_name='heater-detail', required=False)

    class Meta:
        model = Sensor
        fields = ('id', 'hostname', 'name', 'address', 'type', 'freq', 'status', 'gpio', 'rorg', 'rorg_func', 'rorg_type', 'offset', 'room_name', 'ruleset', 'heater', 'last_temperature')

    def get_last_temperature(self, obj):
        last_temperature = obj.get_last_temperature()
        return last_temperature

class TemperatureSerializer(serializers.HyperlinkedModelSerializer):
    sensor = serializers.HyperlinkedRelatedField(view_name='sensor-detail')
    offseted_temp = serializers.DecimalField(required=False)

    class Meta:
        model = Temperature
        fields = ('sensor', 'date', 'temp', 'offseted_temp')

class HeaterSerializer(serializers.HyperlinkedModelSerializer):
    type = serializers.ChoiceField(choices=HEATER_TYPE)
    id = serializers.HyperlinkedIdentityField(view_name='heater-detail')
    gpio = serializers.IntegerField(required=False)
    mode = serializers.ChoiceField(choices=MODE)
    controller = serializers.ChoiceField(choices=HEATER_CONTROLLER)
    state = serializers.SerializerMethodField('get_heater_state')
    last_history = serializers.SerializerMethodField('get_last_history')
    sensors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sensor-detail')

    class Meta:
        model = Heater
        fields = ('id', 'hostname', 'name', 'address', 'type', 'freq', 'status', 'gpio', 'mode', 'description', 'controller', 'hysteresis', 'state', 'last_history', 'sensors')

    def get_heater_state(self, obj):
        state = obj.get_heater_state()
        return state

    def get_last_history(self, obj):
        last_history = obj.get_last_history()
        return last_history

class HeaterHistorySerializer(serializers.HyperlinkedModelSerializer):
    heater = serializers.HyperlinkedRelatedField(view_name='heater-detail')

    class Meta:
        model = Heater_history
        fields = ('id', 'heater', 'date', 'state')

class RuleSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='rule-detail')
    ruleset = serializers.HyperlinkedRelatedField(view_name='ruleset-detail')

    class Meta:
        model = Rule
        fields = ('id', 'ruleset', 'weekday', 'time', 'temp')

class RulesetSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.HyperlinkedIdentityField(view_name='ruleset-detail')
    type = serializers.ChoiceField(choices=RULESET_TYPE)
    active_rule = serializers.SerializerMethodField('get_active_rule')
    rules =  serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='rule-detail')
    sensors = serializers.HyperlinkedRelatedField(many=True, read_only=True, view_name='sensor-detail')

    class Meta:
        model = Ruleset
        fields = ('id', 'name', 'type', 'active_rule', 'rules', 'sensors')

    def get_active_rule(self, obj):
        active_rule = obj.get_active_rule()
        if (active_rule == None):
            return None
        else:
            return active_rule.id

