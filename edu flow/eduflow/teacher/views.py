from django.shortcuts import render
from rest_framework.views import APIView
from .models import TeacherProfile,AssignmentTask
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Q
from student.models import StudentProfile,AssignmentSubmission
from rest_framework.viewsets import ModelViewSet 
from adminuser .models import Course,Chapter,Subject,Lesson
from rest_framework import status
from account.permissions import IsTeacher

# teacher can view and update their profile

from . serializers import TeacherProfileSerislizer

class TeacherPrifileView(APIView):
    permission_classes=[IsTeacher]
    def get(self,request):
        teacher_data=TeacherProfile.objects.filter(user=request.user).first()
        if teacher_data is None:
            return Response("no data found")
        ser=TeacherProfileSerislizer(teacher_data)
        return Response(ser.data,status=status.HTTP_200_OK)
    def patch(self,request):
        teacher_data=TeacherProfile.objects.get(user=request.user)  
        ser=TeacherProfileSerislizer(teacher_data,data=request.data,partial=True,context={'request':request})
        if ser.is_valid():
            ser.save()
            return Response({"data":ser.data,"message": "profile updated successfully"}, status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)



# assignment task for teacher
from .serializers import TaskSerializer
        
class TaskTeacherView(ModelViewSet):
    serializer_class=TaskSerializer
    permission_classes=[IsTeacher]

    def get_queryset(self):
        queryset=AssignmentTask.objects.all()
        keyword=self.request.GET.get('task',None)
        if keyword:
            queryset=AssignmentTask.objects.filter(Q(task_name__istartswith=keyword)| Q(students__full_name__istartswith=keyword))
        return queryset
    


# recorded lesson
from adminuser.serializers import LessonSerializer

class LessonTeacherView(ModelViewSet):
    queryset=Lesson.objects.all()
    serializer_class=LessonSerializer
    permission_classes=[IsTeacher]


 

# assignmen submission teacher view, and update mark
from student.serializers import AssignmentSubmissionSerializer


class SubmissionTeacherView(APIView):
    permission_classes=[IsTeacher]
    def get(self,request):
        keyword=request.GET.get('submission')
        if keyword:
            submitted_data=AssignmentSubmission.objects.filter(Q(student__full_name__istartswith=keyword) | Q(assignment__task_name__istartswith=keyword))
        else:
            submitted_data=AssignmentSubmission.objects.all()
        ser=AssignmentSubmissionSerializer(submitted_data,many=True)
        return Response(ser.data,status=status.HTTP_200_OK)
    def put(self,request):
        k=request.data
        id_=k.get('id')
        if id_ is None:
            return Response("id must be requierd")
        try:
            m=AssignmentSubmission.objects.get(id=id_)
        except AssignmentSubmission.DoesNotExist:
            return Response("no data found")    
        ser=AssignmentSubmissionSerializer(m,k,partial=True, context={'request': request})
        if ser.is_valid():
            ser.save()
            return Response({"data":ser.data,"message": "mark updated successfully"}, status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)