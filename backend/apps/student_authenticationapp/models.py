from django.db import models

# Create your models here.
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
# Create your models here.

YEAR_CHOICES = [
    (1, 'First Year'),
    (2, 'Second Year'),
    (3, 'Third Year'),
    (4, 'Fourth Year')
]

SEMESTER_CHOICES = [
    (1, 'First Semester'),
    (2, 'Second Semester')
]

COURSE_CHOICES = [
    ('CS', 'Computer Science'),
    ('ENG', 'Engineering'),
    ('MED', 'Medicine'),
    ('BUS', 'Business'),
    ('LAW', 'Law'),
]

class Student(AbstractUser):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES,default=1)
    semester = models.IntegerField(choices=SEMESTER_CHOICES,default=1)
    course = models.CharField(max_length=3, choices=COURSE_CHOICES,default="CS")

    groups = models.ManyToManyField(Group, related_name='student_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='student_permissions', blank=True)
    
    def __str__(self):
        return f"{self.username} - Year {self.year_of_study}"