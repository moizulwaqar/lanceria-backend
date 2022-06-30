# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
# from django.contrib.auth.admin import User
from authentication.models import User


def create_superuser(apps, schema_editor):
    superuser = User()
    superuser.is_active = True
    superuser.is_superuser = True
    superuser.is_staff = True
    superuser.username = 'lanceria'
    superuser.email = 'admin@lanceria.com'
    superuser.set_password('lanceria@123')
    superuser.save()


class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_superuser)
    ]
