# Generated by Django 3.1.7 on 2021-07-14 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0002_auto_20210713_0649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='success',
            field=models.CharField(choices=[('70-80', '70-80'), ('80-90', '80-90'), ('90+', '90+'), ('Any', 'Any')], default='Any', max_length=25),
        ),
    ]