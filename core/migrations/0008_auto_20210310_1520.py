# Generated by Django 3.1.4 on 2021-03-10 15:20

from django.db import migrations
import django_dropbox_storage.storage
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20210310_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spectrum',
            name='spec_pic',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 400],upload_to='spec_pics', verbose_name='Upload pic'),
        ),
    ]
