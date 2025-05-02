from rest_framework import serializers
from .models import StudentProfile
from .models import AssignmentSubmission,Leaderboard
from teacher.models import AssignmentTask,TeacherProfile
from adminuser.models import Course
from django.db.models import Q
from account .models import CustomUser





from account.serializers import CustomUserSerializer
from adminuser.serializers import CourseSerializer


class StudentProfileSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    course=serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    class Meta:
        model=StudentProfile
        fields='__all__'
    def to_representation(self, instance):
        return {
            "id":instance.id,
            "course":instance.course.course_name,
            "full_name":instance.full_name,
            "phone_number":instance.phone_number,
        }    
    def create(self, validated_data):
        user_=self.context['request'].user
        full_name_=validated_data.get('full_name')
        phone_number_=validated_data.get('phone_number')
        course_id=validated_data.pop('course')
        try:
            course_=Course.objects.get(id=course_id.id)
        except Course.DoesNotExist:
            raise serializers.ValidationError("no course found")
        new_student=StudentProfile.objects.create(full_name=full_name_, phone_number=phone_number_, course=course_,user=user_)
        user_=new_student.user
        user_.role=CustomUser.STUDENT
        user_.save()
        return new_student  
    def update(self, instance, validated_data):
        instance.full_name=validated_data.get('full_name',instance.full_name)
        instance.phone_number=validated_data.get('phone_number',instance.phone_number)
        course_id=validated_data.get('course')
        if course_id:
            instance.course=Course.objects.get(id=course_id.id)
        instance.save()                
        return instance

from teacher.serializers import TaskSerializer
class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())
    assignment=serializers.PrimaryKeyRelatedField(queryset=AssignmentTask.objects.all())
    class Meta:
        model=AssignmentSubmission
        fields='__all__'  
    def to_representation(self, instance):
        return {
            "id":instance.id,
            "student":instance.student.full_name,
            "assignment":instance.assignment.task_name,
            "file":instance.file.url if instance.file else None,
            "submitted_at":instance.submitted_at,
            "status":instance.status,
            "mark":instance.mark
        }    
    def create(self, validated_data):
        student_=StudentProfile.objects.get(user=validated_data['student'])
        k=AssignmentTask.objects.filter(students__user=validated_data['student']).exclude(blocked_students=student_)
        student_data=validated_data.pop('student')   
        try:
            assignment_data=validated_data.pop('assignment')
        except:
            raise serializers.ValidationError('enter a valid project')
        if assignment_data not in k :
            raise serializers.ValidationError('no matches')
        new_submission=AssignmentSubmission.objects.create(student=student_,assignment=assignment_data,**validated_data)
        return new_submission
    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        if TeacherProfile.objects.filter(user=request_user).exists():
            instance.status=validated_data.get('status',instance.status)
            instance.mark=validated_data.get('mark',instance.mark)
            if instance.mark:
                instance.status='approved'
                leader_mark=instance.mark
                try:
                    leader_student=Leaderboard.objects.get(student_name=instance.student) 
                    leader_student.mark=instance.mark
                    leader_student.save()
                except Leaderboard.DoesNotExist:
                    leader_student=Leaderboard.objects.create(student_name=instance.student,mark=leader_mark)    
            instance.save()
            return instance
        elif instance.student.user==request_user:
            instance.file=validated_data.get('file',instance.file)
            instance.save()
            return instance
        else:
            raise serializers.ValidationError("no data")



    
# users see student leaderboard

class leaderboardserialier(serializers.ModelSerializer):
    class Meta:
        model=Leaderboard
        fields='__all__'

    def to_representation(self, instance):
        return {
            "id":instance.id,
            "mark":instance.mark,
            "student_name":instance.student_name.full_name
        }