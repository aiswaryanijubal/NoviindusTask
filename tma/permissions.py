from rest_framework.permissions import BasePermission


class IsAdminOrSuperAdmin(BasePermission):
    
    def has_permission(self, request):
        return request.user.user_type in ["ADMIN", "SUPERADMIN"]
