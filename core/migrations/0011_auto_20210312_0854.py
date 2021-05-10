# Generated by Django 3.1.4 on 2021-03-12 13:54

from django.db import migrations
import django_dropbox_storage.storage
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_spectrum_pic_path'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spectrum',
            name='spec_pic',
            field=django_resized.forms.ResizedImageField(blank=True, crop=['middle', 'center'], force_format='JPEG', keep_meta=True, null=True, quality=75, size=[600, 400], storage=django_dropbox_storage.storage.DropboxStorage(), upload_to='nirpics', verbose_name='Upload pic'),
        ),
    ]