from django.urls import path,include
from. import views
from rest_framework.routers import DefaultRouter



router = DefaultRouter()
router.register('question', views.TaskTeacherView, basename='question')
router.register('lesson', views.LessonTeacherView, basename='lesson')


urlpatterns = [
    path('profile/',views.TeacherPrifileView.as_view()),
    path('submission/',views.SubmissionTeacherView.as_view()),
    path('task/', include(router.urls))

]
