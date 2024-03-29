# Generated by Django 3.1.7 on 2021-09-16 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bid', '0006_auto_20210915_0709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='amount',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='bid',
            name='paid_type',
            field=models.CharField(choices=[('full_payment', 'full_payment'), ('milestone', 'milestone'), ('perHour', 'perHour')], default='Project', max_length=30),
        ),
    ]
