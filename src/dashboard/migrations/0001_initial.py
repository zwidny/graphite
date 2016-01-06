# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('name', models.CharField(max_length=128, serialize=False, primary_key=True)),
                ('state', models.TextField()),
                ('owners', models.ManyToManyField(related_name='dashboards', to='account.Profile')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('name', models.CharField(max_length=128, serialize=False, primary_key=True)),
                ('state', models.TextField()),
                ('owners', models.ManyToManyField(related_name='templates', to='account.Profile')),
            ],
        ),
    ]
