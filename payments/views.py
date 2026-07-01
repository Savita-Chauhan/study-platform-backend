import razorpay
import hmac
import hashlib
import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Payment
from courses.models import Course, Enrollment

client = razorpay.Client(
    auth=(
        os.getenv('RAZORPAY_KEY_ID'),
        os.getenv('RAZORPAY_KEY_SECRET')
    )
)


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        course_id = request.data.get('course_id')
        try:
            course = Course.objects.get(pk=course_id)

            if Enrollment.objects.filter(student=request.user, course=course).exists():
                return Response({'error': 'Already enrolled!'}, status=status.HTTP_400_BAD_REQUEST)

            if course.is_free:
                return Response({'error': 'This course is free!'}, status=status.HTTP_400_BAD_REQUEST)

            amount = int(course.price * 100)
            order = client.order.create({
                'amount': amount,
                'currency': 'INR',
                'notes': {
                    'course_id': course.id,
                    'user_id': request.user.id,
                }
            })

            Payment.objects.create(
                student=request.user,
                course=course,
                razorpay_order_id=order['id'],
                amount=course.price,
                status='pending'
            )

            return Response({
                'order_id': order['id'],
                'amount': amount,
                'currency': 'INR',
                'course_title': course.title,
                'key': os.getenv('RAZORPAY_KEY_ID'),
            }, status=status.HTTP_201_CREATED)

        except Course.DoesNotExist:
            return Response({'error': 'Course not found!'}, status=status.HTTP_404_NOT_FOUND)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        key_secret = os.getenv('RAZORPAY_KEY_SECRET')
        message = f"{razorpay_order_id}|{razorpay_payment_id}"

        generated_signature = hmac.new(
            key_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        if generated_signature != razorpay_signature:
            return Response({'error': 'Invalid signature!'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(
                razorpay_order_id=razorpay_order_id,
                student=request.user
            )
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'completed'
            payment.save()

            Enrollment.objects.create(
                student=request.user,
                course=payment.course
            )

            return Response({
                'message': 'Payment successful! You are now enrolled.',
                'course_title': payment.course.title,
            })

        except Payment.DoesNotExist:
            return Response({'error': 'Payment not found!'}, status=status.HTTP_404_NOT_FOUND)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        payments = Payment.objects.filter(student=request.user).order_by('-created_at')
        data = [{
            'id': p.id,
            'course': p.course.title,
            'amount': str(p.amount),
            'status': p.status,
            'date': p.created_at,
        } for p in payments]
        return Response(data)