# Generated by Django 3.1.4 on 2021-02-01 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PcaModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(blank=True, null=True)),
                ('component', models.TextField(blank=True, null=True)),
                ('calibration', models.ManyToManyField(to='core.Spectrum')),
            ],
        ),
    ]
