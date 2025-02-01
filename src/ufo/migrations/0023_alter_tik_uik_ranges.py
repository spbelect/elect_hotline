# Generated by Django 5.1.5 on 2025-02-01 08:54

import django.core.serializers.json
import django_pydantic_field.compat.django
import django_pydantic_field.fields
import types
import typing
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ufo', '0022_alter_tik_uik_ranges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tik',
            name='uik_ranges',
            field=django_pydantic_field.fields.PydanticSchemaField(blank=True, config=None, encoder=django.core.serializers.json.DjangoJSONEncoder, null=True, schema=django_pydantic_field.compat.django.GenericContainer(typing.Union, (django_pydantic_field.compat.django.GenericContainer(list, (django_pydantic_field.compat.django.GenericContainer(list, (int,)),)), types.NoneType)), verbose_name='Subordinate UIK numbers'),
        ),
    ]
