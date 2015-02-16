# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


flag_name = 'show_user_actions'
Flag = models.get_app('waffle').Flag


def update_waffle_forward(apps, schema_editor):
    """Create or udpate flag"""
    Flag.objects.update_or_create(
        name=flag_name,
        defaults={
            'superusers': True,
            'everyone': False,
            'note': 'Show WIP user actions/history on user detail page'
        }
    )


def update_waffle_backward(apps, schema_editor):
    """Delete flag"""
    Flag.objects.get(name=flag_name).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0005_auto_20150215_2342'),
    ]

    operations = [
        migrations.RunPython(update_waffle_forward, update_waffle_backward),
    ]
