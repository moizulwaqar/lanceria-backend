# Generated by Django 3.1.7 on 2021-09-15 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bid', '0005_auto_20210913_0739'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bid',
            name='paid_type',
            field=models.CharField(choices=[('Project', 'Project'), ('Mile Stone', 'Mile Stone'), ('Per Hour', 'Per Hour')], default='Project', max_length=30),
        ),
    ]
