# backend/quiz/models.py

from django.db import models
from users.models import CustomUser
from courses.models import Course

class Quiz(models.Model):
    """Har course ke saath ek quiz hoga"""
    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pass_percentage = models.IntegerField(default=70)  # 70% pass hona chahiye
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quiz - {self.course.title}"


class Question(models.Model):
    """Quiz ke andar questions"""
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text[:50]


class Answer(models.Model):
    """Har question ke 4 options hote hain"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)  # Sahi jawab

    def __str__(self):
        return self.answer_text


class QuizAttempt(models.Model):
    """Student ne quiz attempt kiya"""
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    score = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.course.title} - {self.score}%"