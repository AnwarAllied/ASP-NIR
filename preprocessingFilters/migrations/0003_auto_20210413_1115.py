# Generated by Django 3.1.4 on 2021-04-13 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preprocessingFilters', '0002_auto_20210405_1934'),
    ]

    operations = [
        migrations.AddField(
            model_name='sgfilter',
            name='ingrediant',
            field=models.TextField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name='sgfilter',
            name='title',
            field=models.TextField(blank=True, max_length=100, null=True),
        ),
    ]
