# Generated by Django 3.0.5 on 2020-05-17 12:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ufo', '0003_auto_20200515_0721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='join_requests',
        ),
        migrations.AlterField(
            model_name='orgjoinapplication',
            name='organization',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='join_requests', to='ufo.Organization'),
        ),
        migrations.AlterField(
            model_name='orgjoinapplication',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='org_join_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
