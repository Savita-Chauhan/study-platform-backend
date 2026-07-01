# backend/courses/views.py

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Category, Course, Lesson, Enrollment
from .serializers import (
    CategorySerializer, CourseSerializer,
    CourseCreateSerializer, EnrollmentSerializer
)


class CategoryListView(APIView):
    """GET /api/courses/categories/ — sabhi categories"""
    permission_classes = [AllowAny]

    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CourseListView(APIView):
    """GET /api/courses/ — sabhi published courses"""
    permission_classes = [AllowAny]

    def get(self, request):
        courses = Course.objects.filter(is_published=True)

        # Filter by category
        category = request.query_params.get('category')
        if category:
            courses = courses.filter(category__id=category)

        # Filter by level
        level = request.query_params.get('level')
        if level:
            courses = courses.filter(level=level)

        # Filter free courses
        is_free = request.query_params.get('is_free')
        if is_free:
            courses = courses.filter(is_free=True)

        serializer = CourseSerializer(
            courses, many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def post(self, request):
        """POST /api/courses/ — naya course banao (instructor only)"""
        if request.user.role != 'instructor':
            return Response(
                {'error': 'Only instructors can create courses!'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CourseCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            course = serializer.save()
            return Response({
                'message': 'Course created successfully!',
                'course': CourseSerializer(
                    course,
                    context={'request': request}
                ).data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CourseDetailView(APIView):
    """GET /api/courses/<id>/ — ek course ki detail"""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            course = Course.objects.get(pk=pk, is_published=True)
            serializer = CourseSerializer(
                course,
                context={'request': request}
            )
            return Response(serializer.data)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found!'},
                status=status.HTTP_404_NOT_FOUND
            )

    def put(self, request, pk):
        """Course update karo — sirf instructor apna course update kar sakta hai"""
        try:
            course = Course.objects.get(pk=pk, instructor=request.user)
            serializer = CourseCreateSerializer(
                course,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Course updated!'})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found!'},
                status=status.HTTP_404_NOT_FOUND
            )


class EnrollView(APIView):
    """POST /api/courses/<id>/enroll/ — free course mein enroll karo"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)

            # Already enrolled?
            if Enrollment.objects.filter(
                student=request.user,
                course=course
            ).exists():
                return Response(
                    {'error': 'Already enrolled!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Paid course ke liye payment chahiye
            if not course.is_free:
                return Response(
                    {'error': 'This is a paid course. Please make payment first!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            enrollment = Enrollment.objects.create(
                student=request.user,
                course=course
            )
            return Response({
                'message': f'Successfully enrolled in {course.title}!'
            }, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found!'},
                status=status.HTTP_404_NOT_FOUND
            )


class MyCoursesView(APIView):
    """GET /api/courses/my-courses/ — mere enrolled courses"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(student=request.user)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)