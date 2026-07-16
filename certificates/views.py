import os
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Certificate
from courses.models import Course, Enrollment


class GenerateCertificateView(APIView):
    """
    POST /api/certificates/generate/
    Course complete  certificate generated
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')

        try:
            course = Course.objects.get(pk=course_id)

            
            enrollment = Enrollment.objects.filter(
                student=request.user,
                course=course
            ).first()

            if not enrollment:
                return Response(
                    {'error': 'You are not enrolled in this course!'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Already certificate ?
            existing = Certificate.objects.filter(
                student=request.user,
                course=course
            ).first()

            if existing:
                return Response({
                    'message': 'Certificate already exists!',
                    'certificate_id': str(existing.certificate_id),
                    'download_url': f'/api/certificates/download/{existing.certificate_id}/'
                })

            # Certificate record 
            certificate = Certificate.objects.create(
                student=request.user,
                course=course
            )

            # Enrollment complete mark 
            enrollment.is_completed = True
            enrollment.save()

            return Response({
                'message': 'Certificate generated successfully!',
                'certificate_id': str(certificate.certificate_id),
                'download_url': f'/api/certificates/download/{certificate.certificate_id}/'
            }, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response(
                {'error': 'Course not found!'},
                status=status.HTTP_404_NOT_FOUND
            )


class DownloadCertificateView(APIView):
    """
    GET /api/certificates/download/<certificate_id>/
    PDF certificate download karo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, certificate_id):
        try:
            certificate = Certificate.objects.get(
                certificate_id=certificate_id,
                student=request.user
            )

            # PDF genrated
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=landscape(A4))
            width, height = landscape(A4)

            # Background color
            p.setFillColor(colors.HexColor('#1a1a2e'))
            p.rect(0, 0, width, height, fill=True, stroke=False)

            # Border
            p.setStrokeColor(colors.HexColor('#f0c040'))
            p.setLineWidth(4)
            p.rect(20, 20, width-40, height-40, fill=False, stroke=True)

            # Title
            p.setFillColor(colors.HexColor('#f0c040'))
            p.setFont("Helvetica-Bold", 40)
            p.drawCentredString(width/2, height-120, "Certificate of Completion")

            # Subtitle
            p.setFillColor(colors.white)
            p.setFont("Helvetica", 20)
            p.drawCentredString(width/2, height-170, "This is to certify that")

            # Student Name
            p.setFillColor(colors.HexColor('#f0c040'))
            p.setFont("Helvetica-Bold", 35)
            p.drawCentredString(
                width/2, height-230,
                certificate.student.username.upper()
            )

            # Course completion text
            p.setFillColor(colors.white)
            p.setFont("Helvetica", 20)
            p.drawCentredString(
                width/2, height-280,
                "has successfully completed the course"
            )

            # Course Name
            p.setFillColor(colors.HexColor('#f0c040'))
            p.setFont("Helvetica-Bold", 28)
            p.drawCentredString(width/2, height-330, certificate.course.title)

            # Date
            p.setFillColor(colors.white)
            p.setFont("Helvetica", 16)
            date_str = certificate.issued_at.strftime("%B %d, %Y")
            p.drawCentredString(width/2, height-390, f"Issued on: {date_str}")

            # Certificate ID
            p.setFont("Helvetica", 12)
            p.setFillColor(colors.HexColor('#aaaaaa'))
            p.drawCentredString(
                width/2, 60,
                f"Certificate ID: {certificate.certificate_id}"
            )

            # Line decoration
            p.setStrokeColor(colors.HexColor('#f0c040'))
            p.setLineWidth(2)
            p.line(100, height-250, width-100, height-250)
            p.line(100, height-360, width-100, height-360)

            p.save()
            buffer.seek(0)

            # PDF response
            response = HttpResponse(
                buffer.getvalue(),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = (
                f'attachment; filename="certificate_{certificate.certificate_id}.pdf"'
            )
            return response

        except Certificate.DoesNotExist:
            return Response(
                {'error': 'Certificate not found!'},
                status=status.HTTP_404_NOT_FOUND
            )


class MyCertificatesView(APIView):
    """
    GET /api/certificates/
    Mere saare certificates
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(student=request.user)
        data = [{
            'id': str(c.certificate_id),
            'course': c.course.title,
            'issued_at': c.issued_at,
            'download_url': f'/api/certificates/download/{c.certificate_id}/'
        } for c in certificates]
        return Response(data)