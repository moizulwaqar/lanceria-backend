# Generated by Django 3.1.7 on 2021-08-12 11:20

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_auto_20210812_0553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='description',
        ),
        migrations.RemoveField(
            model_name='user',
            name='title',
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('role', models.CharField(blank=True, choices=[('Employer', 'Employer'), ('Freelancer', 'Freelancer')], default='Employer', max_length=25, null=True)),
                ('skill', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1000), blank=True, null=True, size=None)),
                ('title', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_in_user_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
