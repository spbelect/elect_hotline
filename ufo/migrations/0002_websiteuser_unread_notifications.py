# Generated by Django 3.0.5 on 2020-05-15 07:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ufo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteuser',
            name='unread_notifications',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=[]),
        ),
    ]
