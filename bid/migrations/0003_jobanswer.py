# Generated by Django 3.1.7 on 2021-09-13 05:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job', '0010_auto_20210824_0801'),
        ('bid', '0002_auto_20210810_0627'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted_on', models.DateTimeField(blank=True, null=True)),
                ('answer', models.CharField(blank=True, max_length=5000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='job_question_in_job_answer', to='job.jobquestions')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_in_job_answer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-id'],
            },
        ),
    ]
