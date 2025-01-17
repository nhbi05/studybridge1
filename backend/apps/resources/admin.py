from django.contrib import admin
from .models import Resource,Note,Tutorial,CourseUnit
# Register your models here.
#admin.site.register(Resource)
admin.site.register(Note)
admin.site.register(Tutorial)
admin.site.register(CourseUnit)