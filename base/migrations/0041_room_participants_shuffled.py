# Generated by Django 5.1.1 on 2024-09-27 04:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0040_alter_room_matches'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='participants_shuffled',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
