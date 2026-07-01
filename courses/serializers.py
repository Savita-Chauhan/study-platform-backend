# backend/courses/serializers.py

from rest_framework import serializers
from .models import Category, Course, Lesson, Enrollment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_url', 'order']


class CourseSerializer(serializers.ModelSerializer):
    instructor_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    total_lessons = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'instructor_name',
            'category', 'category_name', 'price', 'is_free',
            'thumbnail', 'level', 'is_published', 'lessons',
            'total_lessons', 'is_enrolled', 'created_at'
        ]

    def get_instructor_name(self, obj):
        return obj.instructor.username

    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

    def get_total_lessons(self, obj):
        return obj.lessons.count()

    def get_is_enrolled(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Enrollment.objects.filter(
                student=request.user,
                course=obj
            ).exists()
        return False


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            'title', 'description', 'category',
            'price', 'is_free', 'thumbnail', 'level'
        ]

    def create(self, validated_data):
        # Instructor automatically logged in user hoga
        request = self.context.get('request')
        course = Course.objects.create(
            instructor=request.user,
            **validated_data
        )
        return course


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'enrolled_at', 'is_completed']

    def get_course_title(self, obj):
        return obj.course.title