# Generated by Django 3.1.7 on 2021-07-29 07:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0002_auto_20210729_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicequestion',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='service_in_service_question', to='service.service'),
        ),
    ]
