from django.contrib import admin
from .models import Bid, BidMileStone, JobAnswer

# Register your models here.

admin.site.register(Bid)
admin.site.register(BidMileStone)
admin.site.register(JobAnswer)
