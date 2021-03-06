# Generated by Django 3.2.3 on 2021-08-06 02:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tube', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('dt', models.DateTimeField(default=django.utils.timezone.now, verbose_name='通報日時')),
                ('reason', models.CharField(max_length=200, verbose_name='通報理由')),
                ('report_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_user', to=settings.AUTH_USER_MODEL, verbose_name='通報したユーザー')),
                ('reported_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_user', to=settings.AUTH_USER_MODEL, verbose_name='通報されたユーザー')),
            ],
            options={
                'db_table': 'report',
            },
        ),
    ]
