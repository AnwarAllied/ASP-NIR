# Generated by Django 3.1.4 on 2021-03-11 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20210311_0118'),
    ]

    operations = [
        migrations.AddField(
            model_name='spectrum',
            name='pic_path',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
