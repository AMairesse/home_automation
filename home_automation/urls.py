from django.conf.urls import include, url
from heat_control import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # urls to API
    url(r'^hc/api/sensors/$', views.SensorList.as_view(), name="sensor-list"),
    url(r'^hc/api/sensors/(?P<pk>[0-9]+)/$', views.SensorDetail.as_view(), name="sensor-detail"),
    url(r'^hc/api/temperatures/$', views.TemperatureRecord.as_view(), name="temperature-record"),
    url(r'^hc/api/heaters/$', views.HeaterList.as_view(), name="heater-list"),
    url(r'^hc/api/heaters/(?P<pk>[0-9]+)/$', views.HeaterDetail.as_view(), name="heater-detail"),
    url(r'^hc/api/heaters_history/$', views.HeaterHistoryRecord.as_view(), name="heater_history-record"),
    url(r'^hc/api/rulesets/$', views.RulesetList.as_view(), name="ruleset-list"),
    url(r'^hc/api/rulesets/(?P<pk>[0-9]+)/$', views.RulesetDetail.as_view(), name="ruleset-detail"),
    url(r'^hc/api/rules/$', views.RuleList.as_view(), name="rule-list"),
    url(r'^hc/api/rules/(?P<pk>[0-9]+)/$', views.RuleDetail.as_view(), name="rule-detail"),

    # General site urls
    url(r'^hc$', views.index),
    url(r'^hc/$', views.index),
    url(r'^hc/login$', views.login_user),
    url(r'^hc/ruleset$', views.ruleset),
    url(r'^hc/day_graph/(\d{4})/(\d+)/(\d+)/(\d{4})/(\d+)/(\d+)/$', views.day_graph),
    url(r'^hc/stats$', views.stats),
    url(r'^hc/runtime_graph/(\d{4})/(\d+)/(\d+)/(\d{4})/(\d+)/(\d+)/$', views.runtime_graph),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^hc/admin/', include(admin.site.urls)),
]

