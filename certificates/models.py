# backend/certificates/models.py

from django.db import models
from users.models import CustomUser
from courses.models import Course
import uuid

class Certificate(models.Model):
    """Course complete karne pe certificate milega"""
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    # Unique certificate ID — verify karne ke liye
    certificate_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ('student', 'course')  # Ek course ka ek hi certificate

    def __str__(self):
        return f"{self.student.username} - {self.course.title}"