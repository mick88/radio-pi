# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-04 21:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GpioButton',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bcm_pin', models.PositiveSmallIntegerField(help_text='Pin number in <a href="https://pinout.xyz/" target="_blank">BCM numbering</a>.')),
                ('action', models.CharField(choices=[(b'next', 'Next'), (b'play', 'Play'), (b'previous', 'Previous'), (b'stop', 'Stop'), (b'volume_down', 'Volume Down'), (b'volume_up', 'Volume Up')], max_length=32)),
                ('enable', models.BooleanField(default=True, help_text='Enable this button/pin')),
            ],
        ),
    ]
