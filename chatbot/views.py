import os
from groq import Groq
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from courses.models import Course, Enrollment

client = Groq(api_key=os.getenv('GROQ_API_KEY'))


class ChatbotView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_message = request.data.get('message')
        course_id = request.data.get('course_id')

        if not user_message:
            return Response(
                {'error': 'Message cannot be empty!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            course_context = ""
            if course_id:
                course = Course.objects.get(pk=course_id)
                is_enrolled = Enrollment.objects.filter(
                    student=request.user,
                    course=course
                ).exists()

                if is_enrolled:
                    lessons = course.lessons.all()
                    lessons_content = "\n".join([
                        f"Lesson {l.order}: {l.title}\n{l.content}"
                        for l in lessons
                    ])
                    course_context = f"""
                    Course: {course.title}
                    Description: {course.description}
                    Lessons: {lessons_content}
                    """

            if course_context:
                system_prompt = f"""
                Tu ek helpful study assistant hai.
                Course content: {course_context}
                Student ke questions ka course content ke basis pe answer do.
                """
            else:
                system_prompt = """
                Tu ek helpful study assistant hai.
                Student ke questions ka short aur clear answer do.
                """

            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=1000,
            )

            return Response({
                'message': user_message,
                'response': response.choices[0].message.content,
            }, status=status.HTTP_200_OK)

        except Course.DoesNotExist:
            return Response({'error': 'Course not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'AI error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateQuizView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        topic = request.data.get('topic')
        num_questions = request.data.get('num_questions', 5)

        if not topic:
            return Response({'error': 'Topic is required!'}, status=status.HTTP_400_BAD_REQUEST)

        prompt = f"""
        Topic: {topic}
        {num_questions} multiple choice questions banao.
        Exactly is format mein do — koi extra text mat likho:

        Q1: Question text
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: A

        Q2: Question text
        A) Option 1
        B) Option 2
        C) Option 3
        D) Option 4
        Answer: B
        """

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
            )

            raw_text = response.choices[0].message.content
            questions = []
            blocks = raw_text.strip().split('\n\n')

            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 6:
                    question_text = lines[0].split(': ', 1)[-1]
                    options = {
                        'A': lines[1][3:],
                        'B': lines[2][3:],
                        'C': lines[3][3:],
                        'D': lines[4][3:],
                    }
                    correct = lines[5].split(': ')[-1].strip()
                    questions.append({
                        'question': question_text,
                        'options': options,
                        'correct_answer': correct,
                    })

            return Response({
                'topic': topic,
                'questions': questions,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'AI error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)