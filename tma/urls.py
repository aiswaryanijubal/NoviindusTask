from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from .views import (
    TaskListAPIView, TaskReportAPIView, TaskUpdateAPIView, UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    AssignUserToAdminView, TaskListView,LoginWithJWTView, TaskListView, 
    TaskUpdateView, CustomLoginView, DashboardView, CustomLogoutView,
    TaskCreateView,TaskDeleteView
)


urlpatterns = [
    # APIs
    path('login-jwt/', LoginWithJWTView.as_view(), name='api_login'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/tasks/<int:pk>/report/', TaskReportAPIView.as_view(), name='task-report'),
    path('api/v1/tasks/', TaskListAPIView.as_view(), name='task-list'),
    path('api/v1/tasks/<int:pk>/', TaskUpdateAPIView.as_view(), name='task-update'),
    
    # Templates
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/create/", UserCreateView.as_view(), name="user-create"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user-edit"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user-delete"),
    path("assign-user-to-admin/", AssignUserToAdminView.as_view(), name="assign-user-admin"),
    path("tasks/all/", TaskListView.as_view(), name="task-list"),
    path('tasks/create/', TaskCreateView.as_view(), name='task-create'),
    path("tasks/<int:pk>/edit/", TaskUpdateView.as_view(), name="task-edit"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
]

 