from django.contrib import admin
from .models import Job, JobSkill, JobQuestions
# Register your models here.


class JobSetting(admin.ModelAdmin):
    list_display = ('id', 'title', 'budget', 'level', )
    search_fields = ['title', 'description', 'budget', 'level']


# class JobSkillSetting(admin.ModelAdmin):
#     list_display = ('id', 'skill', 'job' )
#     # search_fields = ['title', 'description', 'budget', 'level']


admin.site.register(JobQuestions)
admin.site.register(JobSkill)
admin.site.register(Job, JobSetting)
