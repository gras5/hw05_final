# Generated by Django 2.2.16 on 2022-05-16 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0017_auto_20220516_2045'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='follow',
            name='% (app_label) s_% (class) s_name_unique',
        ),
        migrations.AddConstraint(
            model_name='follow',
            constraint=models.UniqueConstraint(fields=('user', 'author'), name='% (app_label) s_% (class) s_unique_follow'),
        ),
    ]
