# Generated by Django 5.1.1 on 2024-09-21 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ufo', '0009_alter_region_utc_offset'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='answer',
            constraint=models.CheckConstraint(condition=models.Q(models.Q(('appuser__isnull', True), ('operator__isnull', False)), models.Q(('appuser__isnull', False), ('operator__isnull', True)), _connector='OR'), name='ufo_Answer_appuser_or_operator'),
        ),
    ]
