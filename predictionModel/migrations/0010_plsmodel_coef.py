# Generated by Django 3.1.4 on 2021-02-18 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('predictionModel', '0009_auto_20210217_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='plsmodel',
            name='coef',
            field=models.TextField(blank=True, null=True),
        ),
    ]