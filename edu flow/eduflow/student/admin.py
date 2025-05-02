from django.contrib import admin
from .models import StudentProfile,AssignmentSubmission,Leaderboard

admin.site.register(StudentProfile)
admin.site.register(AssignmentSubmission)
admin.site.register(Leaderboard)

# Register your models here.
