# Generated by Django 4.0.6 on 2023-02-01 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0004_user_friends_alter_post_likes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='friends',
            new_name='following',
        ),
    ]
