# Generated by Django 4.1.3 on 2023-01-20 14:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_alter_youtubevideo_length_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtubevideo',
            name='path',
        ),
    ]