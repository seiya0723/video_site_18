# Generated by Django 3.2.3 on 2021-08-09 01:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tube', '0003_userpolicy'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userpolicy',
            old_name='agree',
            new_name='accept',
        ),
    ]
