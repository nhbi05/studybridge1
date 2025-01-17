from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ('id', 'username', 'email', 'year_of_study', 'semester', 'course')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Student
        fields = ('username', 'email', 'password', 'year_of_study', 'semester', 'course')

    def create(self, validated_data):
        user = Student.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            year_of_study=validated_data['year_of_study'],
            semester=validated_data['semester'],
            course=validated_data['course']
        )
        return user
