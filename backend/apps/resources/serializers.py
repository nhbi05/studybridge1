from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Note, Tutorial, CourseUnit

class BaseResourceSerializer(serializers.ModelSerializer):
    course_display = serializers.CharField(source='get_course_display', read_only=True)
    year_display = serializers.CharField(source='get_year_of_study_display', read_only=True)
    semester_display = serializers.CharField(source='get_semester_display', read_only=True)
    uploaded_by_username = serializers.CharField(source='uploaded_by.username', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        fields = '__all__'
        read_only_fields = ('upload_date', 'uploaded_by')

class CourseUnitSerializer(BaseResourceSerializer):
    class Meta(BaseResourceSerializer.Meta):
        model = CourseUnit
        fields = ['id', 'name', 'course', 'course_display', 'year_of_study', 
                 'year_display', 'semester', 'semester_display']

class NoteSerializer(BaseResourceSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta(BaseResourceSerializer.Meta):
        model = Note

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url') and request:
            return request.build_absolute_uri(obj.file.url)
        return None

    def validate_file(self, value):
        # Add file validation if needed
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError('File size cannot exceed 50MB.')
        return value

class TutorialSerializer(BaseResourceSerializer):
    tutorial_type_display = serializers.CharField(source='get_tutorial_type_display', read_only=True)

    class Meta(BaseResourceSerializer.Meta):
        model = Tutorial

    def validate(self, data):
        tutorial_type = data.get('tutorial_type')
        video_url = data.get('video_url')
        scheduled_time = data.get('scheduled_time')

        if tutorial_type == 'video':
            if not video_url:
                raise serializers.ValidationError({
                    'video_url': 'Video URL is required for video tutorials.'
                })
        elif tutorial_type == 'live':
            if not scheduled_time:
                raise serializers.ValidationError({
                    'scheduled_time': 'Scheduled time is required for live sessions.'
                })

        return data