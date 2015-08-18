from heat_control.models import Sensor, Heater, Ruleset, Rule
from django.contrib import admin

class RuleInline(admin.TabularInline):
    model = Rule
    ordering = ('weekday', 'time')
    extra = 0

class SensorAdmin(admin.ModelAdmin):
    fields = ['type', 'hostname', 'name', 'address', 'freq', 'status', 'gpio', 'rorg', 'rorg_func', 'rorg_type', 'offset', 'room_name', 'ruleset', 'heater']
    list_display = ('hostname', 'name', 'type', 'freq', 'room_name')

class HeaterAdmin(admin.ModelAdmin):
    fields = ['type', 'hostname', 'name', 'address', 'freq', 'status', 'gpio', 'mode', 'description', 'controller', 'hysteresis']
    list_display = ('hostname', 'name', 'type', 'description')

class RulesetAdmin(admin.ModelAdmin):
    fields = ['name', 'type']
    inlines = [RuleInline]
    list_display = ('name', 'type')

admin.site.register(Sensor, SensorAdmin)
admin.site.register(Heater, HeaterAdmin)
admin.site.register(Ruleset, RulesetAdmin)
