# Generated by Django 4.2.18 on 2025-01-17 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('MEMBER', 'Member'), ('MODERATOR', 'Moderator'), ('ADMIN', 'Admin')], default='MEMBER', max_length=10)),
                ('joined_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudyGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('course', models.CharField(choices=[('CS', 'Computer Science'), ('ENG', 'Engineering'), ('MED', 'Medicine'), ('BUS', 'Business'), ('LAW', 'Law')], max_length=100)),
                ('year_of_study', models.IntegerField(choices=[(1, 'First Year'), (2, 'Second Year'), (3, 'Third Year'), (4, 'Fourth Year')])),
                ('semester', models.IntegerField(choices=[(1, 'First Semester'), (2, 'Second Semester')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_private', models.BooleanField(default=False)),
                ('max_members', models.IntegerField(default=50)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_groups', to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(related_name='joined_groups', through='study_group.GroupMembership', to=settings.AUTH_USER_MODEL)),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resources.courseunit')),
            ],
        ),
        migrations.CreateModel(
            name='GroupResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('file', models.FileField(upload_to='group_resources/')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study_group.studygroup')),
                ('uploaded_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-upload_date'],
            },
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study_group.studygroup'),
        ),
        migrations.AddField(
            model_name='groupmembership',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='GroupDiscussion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_pinned', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study_group.studygroup')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='DiscussionComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('discussion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='study_group.groupdiscussion')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='groupmembership',
            unique_together={('user', 'group')},
        ),
    ]