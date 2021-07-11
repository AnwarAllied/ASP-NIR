# Generated by Django 3.1.4 on 2021-07-10 22:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20210710_1701'),
        ('spectraModelling', '0004_auto_20210511_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='owner',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.owner'),
        ),
    ]
