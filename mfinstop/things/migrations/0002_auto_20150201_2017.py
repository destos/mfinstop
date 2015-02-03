# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='motiveperiod',
            options={'get_latest_by': 'starts'},
        ),
        migrations.AlterModelOptions(
            name='usermotive',
            options={},
        ),
        migrations.AlterField(
            model_name='thing',
            name='behavior',
            field=models.PositiveSmallIntegerField(default=0, choices=[(1, b'start'), (0, b'stop')]),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='thing',
            unique_together=set([]),
        ),
        migrations.AlterUniqueTogether(
            name='usermotive',
            unique_together=set([('user', 'thing')]),
        ),
    ]
