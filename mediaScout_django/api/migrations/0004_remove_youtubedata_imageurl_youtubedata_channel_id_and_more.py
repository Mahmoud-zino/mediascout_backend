# Generated by Django 4.1.3 on 2023-01-09 12:17

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_user_options_alter_user_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='youtubedata',
            name='imageUrl',
        ),
        migrations.AddField(
            model_name='youtubedata',
            name='channel_id',
            field=models.CharField(default=None, max_length=24),
        ),
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(default=None, max_length=50, validators=[django.core.validators.MaxLengthValidator(50, 'NAME_MAX_ERROR'), django.core.validators.MinLengthValidator(3, 'NAME_MIN_ERROR')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='youtube',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='api.youtubedata'),
        ),
        migrations.AlterField(
            model_name='youtubedata',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
