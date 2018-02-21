from django.contrib import admin
from .models import EnrollWareGroup, EnrollClassTime, EnrollWareCredentials, AHACredentials, Mapper


admin.site.register(EnrollWareGroup)
admin.site.register(EnrollClassTime)
admin.site.register(EnrollWareCredentials)
admin.site.register(AHACredentials)
admin.site.register(Mapper)