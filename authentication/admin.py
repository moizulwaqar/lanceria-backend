from django.contrib import admin
from .models import User, UserProfile

# Register your models here.


class UserSetting(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'provider', 'first_name', 'last_name')
    search_fields = ['username', 'email', 'first_name', 'last_name', ]

    def get_queryset(self, request):
        # qs = super(CertificationSetting, self).get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return User.objects.all()


admin.site.register(User, UserSetting)


class UserProfileSetting(admin.ModelAdmin):
    list_display = ('id', 'role', 'title', 'description')
    search_fields = ['role', 'title', 'description']

    def get_queryset(self, request):
        # qs = super(CertificationSetting, self).get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return UserProfile.objects.all()


admin.site.register(UserProfile, UserProfileSetting)
