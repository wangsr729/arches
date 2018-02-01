# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-01-25 15:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('models', '2337_fuzzy_dates'),
    ]

    def add_permissions(apps, schema_editor, with_create_permissions=True):
        db_alias = schema_editor.connection.alias
        Group = apps.get_model("auth", "Group")
        Permission = apps.get_model("auth", "Permission")
        User = apps.get_model("auth", "User")

        resource_reviewer_group = Group.objects.using(db_alias).create(name='Resource Reviewer')
        read_nodegroup = Permission.objects.get(codename='read_nodegroup', content_type__app_label='models', content_type__model='nodegroup')
        resource_reviewer_group.permissions.add(read_nodegroup)

        try:
            admin_user = User.objects.using(db_alias).get(username='admin')
            admin_user.groups.add(resource_reviewer_group)
            print 'added admin group'
        except Exception as e:
            print e

    def remove_permissions(apps, schema_editor, with_create_permissions=True):
        db_alias = schema_editor.connection.alias
        Group = apps.get_model("auth", "Group")
        resource_reviewer_group = Group.objects.using(db_alias).get(name='Resource Reviewer')
        User = apps.get_model("auth", "User")

        try:
            admin_user = User.objects.using(db_alias).get(username='admin')
            admin_user.groups.remove(resource_reviewer_group)
            print 'removed admin group'
        except:
            pass

        resource_reviewer_group.delete()

    operations = [
        migrations.CreateModel(
            name='ProvisionalEdit',
            fields=[
                ('tile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='provisionaledit', serialize=False, to='models.TileModel')),
                ('status', models.TextField(choices=[('review', 'review'), ('approved', 'approved'), ('rejected', 'rejected')])),
                ('action', models.TextField(choices=[('created', 'created'), ('updated', 'updated'), ('deleted', 'deleted')])),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('reviewtimestamp', models.DateTimeField(blank=True, null=True)),
                ('editor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='editor', to=settings.AUTH_USER_MODEL)),
                ('prototile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='models.TileModel')),
                ('reviewer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewer', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'provisional_edits',
                'managed': True,
            },
        ),
        migrations.RunPython(add_permissions, reverse_code=remove_permissions),
    ]
