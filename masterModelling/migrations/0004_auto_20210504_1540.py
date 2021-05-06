# Generated by Django 3.1.4 on 2021-05-04 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('masterModelling', '0003_auto_20210331_1222'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ingredientsmodel',
            old_name='name',
            new_name='origin',
        ),
        migrations.RenameField(
            model_name='staticmodel',
            old_name='component',
            new_name='applied_model',
        ),
        migrations.RemoveField(
            model_name='ingredientsmodel',
            name='component',
        ),
        migrations.RemoveField(
            model_name='staticmodel',
            name='name',
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='applied_model',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='n_comp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='predected_values',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='preprocessed',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='title',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='trans',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='true_values',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ingredientsmodel',
            name='validation',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='n_comp',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='preprocessed',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='profile',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='spectra',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='title',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='staticmodel',
            name='trans',
            field=models.TextField(blank=True, null=True),
        ),
    ]