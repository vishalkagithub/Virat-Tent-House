from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin

def role_required(allowed_roles):
    """
    Decorator for views that checks if the logged-in user belongs to allowed roles.
    Superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access this page.")
            raise PermissionDenied
        return _wrapped_view
    return decorator

def owner_required(view_func):
    return role_required(['super_admin', 'owner'])(view_func)

def manager_required(view_func):
    return role_required(['super_admin', 'owner', 'manager'])(view_func)

def staff_required(view_func):
    return role_required(['super_admin', 'owner', 'manager', 'staff'])(view_func)

def customer_required(view_func):
    return role_required(['customer'])(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        messages.error(self.request, "Access denied. Insufficient permissions.")
        raise PermissionDenied
