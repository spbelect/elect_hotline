# Generated by Django 5.1.5 on 2025-03-06 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufo', '0026_quiztopic_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='websiteuser',
            name='num_login_emails_sent',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
