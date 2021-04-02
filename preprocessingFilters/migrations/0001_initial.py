# Generated by Django 3.1.4 on 2021-03-31 21:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0004_auto_20210316_1314'),
    ]

    operations = [
        migrations.CreateModel(
            name='SgFilter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('window_length', models.IntegerField(default=13)),
                ('polyorder', models.IntegerField(default=2)),
                ('deriv', models.IntegerField(default=2)),
                ('mode', models.CharField(choices=[('M', 'Mirror'), ('C', 'Constant'), ('N', 'nearest'), ('W', 'wrap'), ('I', 'Interp')], default='M', max_length=1)),
                ('y_axis', models.TextField(blank=True, null=True)),
                ('nirprofile', models.ManyToManyField(to='core.NirProfile')),
            ],
        ),
    ]
