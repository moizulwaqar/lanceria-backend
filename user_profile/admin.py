from django.contrib import admin
from .models import Education, Experience, Skill, Portfolio, LinkedAccount, Language, Certification, UserSkill
# Register your models here.


class EducationSetting(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'institute', )
    search_fields = ['title', 'description', 'institute',]


# class UserSkillSetting(admin.ModelAdmin):
#     list_display = ('id', 'skill')
#     search_fields = ['skill']


class ExperienceSetting(admin.ModelAdmin):
    list_display = ('id', 'title', "country" )
    search_fields = ['title', "country",]


class SkillSetting(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name']


class PortfolioSetting(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    search_fields = ['title', 'description']


class LinkedAccountSetting(admin.ModelAdmin):
    list_display = ('id', 'url')
    search_fields = ['url']


class LanguageSetting(admin.ModelAdmin):
    list_display = ('id', 'name', 'level')
    search_fields = ['name', 'level']


class CertificationSetting(admin.ModelAdmin):
    list_display = ('id', 'name', 'provider_name', 'description')
    search_fields = ['name', 'provider_name', 'description']

    # def get_queryset(self, request):
    #     # qs = super(CertificationSetting, self).get_queryset(request)
    #     # if request.user.is_superuser:
    #     #     return qs
    #     return Certification.original_objects.all()


admin.site.register(Skill, SkillSetting)
admin.site.register(Education, EducationSetting)
admin.site.register(Experience, ExperienceSetting)
admin.site.register(Portfolio, PortfolioSetting)
admin.site.register(LinkedAccount, LinkedAccountSetting)
admin.site.register(Language, LanguageSetting)
admin.site.register(Certification, CertificationSetting)
admin.site.register(UserSkill)
