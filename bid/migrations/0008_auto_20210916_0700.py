# Generated by Django 3.1.7 on 2021-09-16 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bid', '0007_auto_20210916_0657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bidmilestone',
            name='amount',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
