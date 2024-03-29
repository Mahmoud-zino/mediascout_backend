# Generated by Django 4.1.3 on 2023-01-20 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_youtubevideo_length_youtubevideo_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='youtubevideo',
            name='length',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='publish_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AlterField(
            model_name='youtubevideo',
            name='title',
            field=models.CharField(default=None, max_length=100, null=True),
        ),
    ]
