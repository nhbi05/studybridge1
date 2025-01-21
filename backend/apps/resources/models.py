from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

# Define choices for academic years
YEAR_CHOICES = [
    (1, "First Year"),
    (2, "Second Year"),
    (3, "Third Year"),
    (4, "Fourth Year")
]

# Define choices for semesters
SEMESTER_CHOICES = [
    (1, "First Semester"),
    (2, "Second Semester")
]

# Define choices for courses
COURSE_CHOICES = [
    ("CS", "Computer Science"),
    ("ENG", "Engineering"),
    ("MED", "Medicine"),
    ("BUS", "Business"),
    ("LAW", "Law"),
]

# Custom user model extending AbstractUser
class User(AbstractUser):
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='resources_user_set',  # Updated related_name
        blank=True,
        # Help text for user groups
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='resources_user_set',  # Updated related_name
        blank=True,
        help_text='Specific permissions for this user.'
    )
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)

# Model representing a course unit
class CourseUnit(models.Model):
    name = models.CharField(max_length=200)
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    
    def __str__(self):
        return f"{self.name} - {self.get_course_display()}, Year {self.year_of_study}"
    
    class Meta:
        ordering = ['course', 'year_of_study', 'semester', 'name']

# Base class for resources
class Resource(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.CharField(max_length=100, choices=COURSE_CHOICES)
    year_of_study = models.IntegerField(choices=YEAR_CHOICES)
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    subject = models.ForeignKey(CourseUnit, on_delete=models.CASCADE)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.get_course_display()}, Year {self.year_of_study}"

    class Meta:
        abstract = True  # This makes Resource an abstract base class, not a model itself

# Model for notes, inheriting from Resource
class Note(Resource):
    file = models.FileField(upload_to='notes/')
    
    class Meta:
        ordering = ['-upload_date']

from django.core.exceptions import ValidationError

# Model for tutorials, inheriting from Resource
class Tutorial(Resource):
    TUTORIAL_TYPES = [
        ('video', 'Video Tutorial'),
        ('live', 'Live Session')
    ]
    
    tutorial_type = models.CharField(max_length=5, choices=TUTORIAL_TYPES)
    video_url = models.URLField(blank=True, null=True)
    scheduled_time = models.DateTimeField(null=True, blank=True)

    def clean(self):
        if self.tutorial_type == 'video' and not self.video_url:
            raise ValidationError("Video tutorials must have a video URL.")
        if self.tutorial_type == 'live' and not self.scheduled_time:
            raise ValidationError("Live sessions must have a scheduled time.")
