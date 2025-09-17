from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy


from tma.serializers import TaskListSerializer
from tma.permissions import IsAdminOrSuperAdmin
from .models import CustomUser, Task, AdminManage



class LoginWithJWTView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            

            response_data = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "message": "Login successful",
                "name": user.name,
                "username": user.username,
                "user_type": user.user_type,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)



class TaskListView(generics.ListAPIView):
    serializer_class=TaskListSerializer
    permission_class=[IsAuthenticated]
    
    
    def get_queryset(self):
        return Task.objects.filter(assigned_to=self.request.user)
    

class TaskUpdateView(generics.UpdateAPIView):
    serializer_class = TaskListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()

    def update(self, request, *args, **kwargs):
        task = self.get_object()

        
        if task.assigned_to != request.user:
            return Response({"error": "You cannot update this task."}, status=status.HTTP_403_FORBIDDEN)

        status_value = request.data.get("status")
        completion_report = request.data.get("completion_report")
        worked_hours = request.data.get("worked_hours")

        if status_value == "COMPLETED":
            if not completion_report or not worked_hours:
                return Response(
                    {"error": "Completion report and worked hours are required when marking task as completed."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            task.completion_report = completion_report
            task.worked_hours = worked_hours

        task.status = status_value
        task.save()

        return Response(TaskListSerializer(task).data, status=status.HTTP_200_OK)
    


class TaskReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)

        if task.status != "COMPLETED":
            return Response({"error": "Task is not completed yet"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "task": task.title,
            "assigned_to": task.assigned_to.username,
            "completion_report": task.completion_report,
            "worked_hours": task.worked_hours
        })


class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    

class CustomLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect("login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "" 
    
    
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("login")

        if user.user_type not in ["SUPERADMIN", "ADMIN"]:
            logout(request)
            return redirect("login")

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        user = self.request.user
        
        if not user.is_authenticated:
            return ["registration/login.html"]
        
        if user.user_type == "SUPERADMIN":
            return ["admin_panel/superadmin/super-admin-dashboard.html"]
        
        return ["admin_panel/admin/admin-dashboard.html"]
        

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.user_type == "SUPERADMIN":
            context["tasks"] = Task.objects.all()
            context["users"] = CustomUser.objects.filter(user_type='USER')
            context["admins"]= CustomUser.objects.filter(user_type='ADMIN')
        elif user.user_type == "ADMIN":
            user_ids = user.assigned_users.values_list("id", flat=True)
            print(user_ids)
            context["tasks"] = Task.objects.filter(assigned_to_id__in=user_ids)
            

        return context



class UserListView(ListView):
    model = CustomUser
    template_name = "admin_panel/superadmin/user_list.html"
    context_object_name = "users"


class UserCreateView(CreateView):
    model = CustomUser
    fields = ["username",  "password", "user_type"]
    template_name = "admin_panel/superadmin/user_form.html"
    success_url = reverse_lazy("dashboard")

class UserUpdateView(UpdateView):
    model = CustomUser
    fields = ["username",  "user_type"]
    template_name = "admin_panel/superadmin/user_form.html"
    success_url = reverse_lazy("user-list")

class UserDeleteView(DeleteView):
    model = CustomUser
    template_name = "admin_panel/superadmin/user_confirm_delete.html"
    success_url = reverse_lazy("user-list")


class AssignUserToAdminView(CreateView):
    model = AdminManage
    fields = ["admin", "user"]
    template_name = "admin_panel/superadmin/assign_user_form.html"
    success_url = reverse_lazy("dashboard")


class TaskListView(ListView):
    model = Task
    template_name = "admin_panel/superadmin/task_list.html"
    context_object_name = "tasks"



class TaskCreateView(CreateView):
    model = Task
    fields = ['title', 'assigned_to', 'status', 'due_date', 'completion_report', 'worked_hours']
    template_name = "admin_panel/superadmin/task_form.html"  
    success_url = reverse_lazy('task-list')  
    
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        user = self.request.user

        if user.user_type == "SUPERADMIN":
            form.fields["assigned_to"].queryset = CustomUser.objects.filter(user_type="USER")
        elif user.user_type == "ADMIN":
            user_ids = AdminManage.objects.filter(admin=user).values_list("user_id", flat=True)
            form.fields["assigned_to"].queryset = CustomUser.objects.filter(id__in=user_ids)

        return form
        

class TaskUpdateView(UpdateView):
    model = Task
    template_name = "admin_panel/superadmin/task_form.html"
    fields = ["title", "assigned_to", "status", "due_date"]
    success_url = reverse_lazy("task-list")

class TaskDeleteView(DeleteView):
    model = Task
    template_name = "admin_panel/superadmin/task_confirm_delete.html"
    success_url = reverse_lazy("task-list")
