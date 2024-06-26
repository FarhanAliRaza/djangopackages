# Generated by Django 5.0.3 on 2024-04-16 12:07

import django.db.models.deletion
import django_extensions.db.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_remove_profile_google_code_url_profile_gitlab_url_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExtraField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('label', models.CharField(max_length=256)),
                ('url', models.URLField(max_length=256)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
