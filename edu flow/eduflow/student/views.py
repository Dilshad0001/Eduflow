from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .models import AssignmentSubmission,StudentProfile,Leaderboard
from rest_framework.permissions import IsAuthenticated,AllowAny
from. serializers import StudentProfileSerializer
from adminuser.models import Lesson
from rest_framework.response import Response
from teacher.models import AssignmentTask
from rest_framework import status
from account .models import CustomUser
from account .permissions import IsStudent
from django.db.models import Q



class StudentProfileStudentView(ModelViewSet):
    serializer_class=StudentProfileSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        queryset=StudentProfile.objects.filter(user=self.request.user)
        return queryset
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
 

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        serializer.save()



# students get recorderd videos
from adminuser.serializers import LessonSerializer

class LessonStudentView(APIView):
    permission_classes=[IsStudent]
    def get(self,request):
        student_=StudentProfile.objects.get(user=request.user)   
        student_course=student_.course
        k=Lesson.objects.filter(Q(chapter__subject__course__course_name=student_course)& Q(is_approved=True))
        ser=LessonSerializer(k,many=True)
        return Response(ser.data,status=status.HTTP_200_OK)
    

# assignment task students view  
from teacher.serializers import TaskSerializer

class TaskStudentsView(APIView):
    permission_classes=[IsStudent]
    def get(self,request):
        student_=StudentProfile.objects.get(user=request.user)
        k=AssignmentTask.objects.filter(students=student_).exclude(blocked_students=student_) 
        
        print("students in views", k)
        ser=TaskSerializer(k, many=True,context={'user': request.user})
        return Response(ser.data,status=status.HTTP_200_OK)

# assignment submission for student

from .serializers import AssignmentSubmissionSerializer

class SubmissionStudentsView(APIView):
    permission_classes=[IsStudent]
    def get(self,request):
        k=AssignmentSubmission.objects.filter(student__user=request.user)
  
        ser=AssignmentSubmissionSerializer(k,many=True)
        return Response(ser.data,status=status.HTTP_200_OK)
    def post(self,request):
        data_=request.data
        
        ser = AssignmentSubmissionSerializer(data=data_, context={'request': request})
        if ser.is_valid():
            ser.save()
            return Response({"data": ser.data, "message": "assignment added successfully"}, status=status.HTTP_201_CREATED)

        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)
    def put(self,request):
        updated_data=request.data
        id_=updated_data.get('id')
        if id_ is None:
            return Response({"error": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            old_data=AssignmentSubmission.objects.get(id=id_)
        except AssignmentSubmission.DoesNotExist:
            return Response('no data found')
        ser=AssignmentSubmissionSerializer(old_data,data=updated_data,partial=True,context={'request': request})
        if ser.is_valid():
            ser.save()
            return Response({"data":ser.data,"message": "submitted assignment updated successfully"}, status=status.HTTP_200_OK)
        return Response(ser.errors,status=status.HTTP_400_BAD_REQUEST)

# leaderboard

from .serializers import leaderboardserialier

class LeaderBoardView(APIView):
    permission_classes=[AllowAny]
    def get(self,request):
        k=Leaderboard.objects.order_by('-mark')[:3]
        print(k)
        ser=leaderboardserialier(k,many=True)
        k=ser.data
        try:
           k0=(k[0])
        except:
           k0=None   
        try:
           k1=(k[1])
        except:
           k1=None    
        try:
           k2=(k[2])
        except:
           k2=None 
        return Response({
            
            "First rank": k0,
            "Second rank": k1,
            "Third rank": k2
        })

