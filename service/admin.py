from django.contrib import admin
from .models import Service, Gallery, ServiceQuestion, ServiceAnswer

# Register your models here.
admin.site.register(Service)
admin.site.register(Gallery)
admin.site.register(ServiceQuestion)
admin.site.register(ServiceAnswer)
