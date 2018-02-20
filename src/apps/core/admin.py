from django.contrib import admin
from .models import EnrollWareGroup, EnrollClassTime, EnrollWareCredentials, AHACredentials


admin.site.register(EnrollWareGroup)
admin.site.register(EnrollClassTime)
admin.site.register(EnrollWareCredentials)
admin.site.register(AHACredentials)