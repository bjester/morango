# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-27 16:58
from __future__ import unicode_literals

from django.db import migrations
from django.db import models

import morango.models.fields.uuids


class Migration(migrations.Migration):

    dependencies = [("morango", "0011_sharedkey")]

    operations = [
        migrations.CreateModel(
            name="HardDeletedModels",
            fields=[
                (
                    "id",
                    morango.models.fields.uuids.UUIDField(primary_key=True, serialize=False),
                ),
                ("profile", models.CharField(max_length=40)),
            ],
        ),
        migrations.AddField(
            model_name="buffer",
            name="hard_deleted",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="store",
            name="hard_deleted",
            field=models.BooleanField(default=False),
        ),
    ]
