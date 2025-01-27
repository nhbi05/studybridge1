from django.urls import path
from .views import note_list, tutorial_list, dashboard_view, user_info, note_detail, course_unit_list

# URLs configuration
urlpatterns = [  
    path('user/info/', user_info, name='user_info'),
    path('notes/', note_list, name='note_list'),
    path('notes/add/', note_list, name='note_add'),  # URL for adding a new note
    path('tutorials/', tutorial_list, name='tutorial_list'),
    path('tutorials/add/', tutorial_list, name='tutorial_add'),  # URL for adding a new tutorial
    path('course-units/', course_unit_list, name='course_unit_list'),
    path('dashboard/', dashboard_view, name='dashboard_view'),
    path('notes/<int:pk>/', note_detail, name='note_detail'),
]
