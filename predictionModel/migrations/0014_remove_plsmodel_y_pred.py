# Generated by Django 3.1.4 on 2021-02-26 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('predictionModel', '0013_plsmodel_y_pred'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plsmodel',
            name='y_pred',
        ),
    ]
