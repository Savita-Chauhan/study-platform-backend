# backend/courses/urls.py

from django.urls import path
from .views import (
    CategoryListView, CourseListView,
    CourseDetailView, EnrollView, MyCoursesView
)

urlpatterns = [
    path('', CourseListView.as_view(), name='course-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('my-courses/', MyCoursesView.as_view(), name='my-courses'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('<int:pk>/enroll/', EnrollView.as_view(), name='enroll'),
]