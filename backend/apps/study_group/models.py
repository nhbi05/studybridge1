from django.db import models
from django.conf import settings
from apps.resources.models import CourseUnit, COURSE_CHOICES, YEAR_CHOICES, SEMESTER_CHOICES

# Create your models here.

class StudyGroup(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    subject = models.ForeignKey(CourseUnit, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, 
                                 on_delete=models.CASCADE,
                                 related_name='created_groups')
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, 
                                   through='GroupMembership',
                                   related_name='joined_groups')
    created_at = models.DateTimeField(auto_now_add=True)
    is_private = models.BooleanField(default=False)
    max_members = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.name} - {self.get_course_display()}"


class GroupMembership(models.Model):
    ROLE_CHOICES = [
        ('MEMBER', 'Member'),
        ('MODERATOR', 'Moderator'),
        ('ADMIN', 'Admin'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'group']

class GroupResource(models.Model):
    """Model for resources shared specifically within a study group"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='group_resources/')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.group.name}"

    class Meta:
        ordering = ['-upload_date']

class GroupDiscussion(models.Model):
    """Model for group discussions/threads"""
    title = models.CharField(max_length=200)
    content = models.TextField()
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_pinned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - {self.group.name}"

    class Meta:
        ordering = ['-created_at']

class DiscussionComment(models.Model):
    """Model for comments in group discussions"""
    discussion = models.ForeignKey(GroupDiscussion, on_delete=models.CASCADE)
    content = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']