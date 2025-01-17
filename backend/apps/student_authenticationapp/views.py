from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Student
from django.core.validators import validate_email

@api_view(['POST'])
@permission_classes([AllowAny])
def register_student(request):
    try:
        # Extract data with defaults to None
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')
        year_of_study = request.data.get('year_of_study')
        semester = request.data.get('semester')
        course = request.data.get('course')

        # Validate required fields
        if not all([email, password, name, year_of_study, semester, course]):
            return Response(
                {'error': 'All fields are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return Response(
                {'error': 'Invalid email format'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if email already exists
        if Student.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the student user
        student = Student.objects.create_user(
            username=email,
            email=email,
            password=password,
            name=name,
            year_of_study=year_of_study,
            semester=semester,
            course=course
        )

        # Return success response with user data
        return Response({
            'message': 'Registration successful',
            'user': {
                'id': student.id,
                'email': student.email,
                'name': student.name,
                'course': student.get_course_display(),
                'year': student.get_year_of_study_display(),
                'semester': student.get_semester_display()
            }
        }, status=status.HTTP_201_CREATED)

    except IntegrityError as e:
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'An unexpected error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_student(request):
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Authenticate student
        student = authenticate(username=email, password=password)
        
        if student:
            login(request, student)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': student.id,
                    'email': student.email,
                    'name': student.name,
                    'course': student.get_course_display(),
                    'year': student.get_year_of_study_display(),
                    'semester': student.get_semester_display()
                }
            })
        
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    except Exception as e:
        return Response(
            {'error': 'An unexpected error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def logout_student(request):
    try:
        logout(request)
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response(
            {'error': 'An unexpected error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_current_user(request):
    if request.user.is_authenticated:
        student = request.user
        return Response({
            'id': student.id,
            'email': student.email,
            'name': student.name,
            'course': student.get_course_display(),
            'year': student.get_year_of_study_display(),
            'semester': student.get_semester_display()
        })
    return Response(
        {'error': 'Not authenticated'},
        status=status.HTTP_401_UNAUTHORIZED
    )