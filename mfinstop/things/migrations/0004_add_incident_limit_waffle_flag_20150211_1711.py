# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


flag_name = 'limit_incident_logging_hourly'
Flag = models.get_app('waffle').Flag


def update_waffle_forward(apps, schema_editor):
    """Create or udpate flag"""
    Flag.objects.update_or_create(
        name=flag_name,
        defaults={
            'superusers': True,
            'everyone': True,
            'note': 'When incidents are reported, rate limit creation to hour increments'
        }
    )


def update_waffle_backward(apps, schema_editor):
    """Delete flag"""
    Flag.objects.get(name=flag_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0003_auto_20150208_2317'),
    ]

    operations = [
        migrations.RunPython(update_waffle_forward, update_waffle_backward),
    ]
