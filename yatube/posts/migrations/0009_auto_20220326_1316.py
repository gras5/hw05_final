# Generated by Django 2.2.9 on 2022-03-26 10:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20220326_0106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Укажите к какой группе относится пост', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа'),
        ),
    ]
