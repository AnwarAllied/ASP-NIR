# Generated by Django 3.1.4 on 2021-02-16 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictionModel', '0006_remove_plsmodel_component'),
    ]

    operations = [
        migrations.AddField(
            model_name='plsmodel',
            name='mse',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
