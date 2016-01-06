# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('when', models.DateTimeField()),
                ('what', models.CharField(max_length=255)),
                ('data', models.TextField(blank=True)),
                ('tags', tagging.fields.TagField(default=b'', max_length=255, blank=True)),
            ],
        ),
    ]
