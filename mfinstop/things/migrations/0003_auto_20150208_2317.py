# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('things', '0002_auto_20150201_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermotive',
            name='user',
            field=models.ForeignKey(related_name='motives', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
