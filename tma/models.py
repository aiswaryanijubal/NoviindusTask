from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("User must have an username")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')

        return self.create_user(username, password, **extra_fields)
    
       

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_ADMIN = 'SUPERADMIN'
    USER_TYPE_COMPANY = 'ADMIN'
    USER_TYPE_SECURITY = 'USER'

    USER_TYPE_CHOICES = [
        (USER_TYPE_ADMIN, 'superadmin'),
        (USER_TYPE_COMPANY, 'admin'),
        (USER_TYPE_SECURITY, 'user'),
    ]

    name = models.CharField(max_length=100)
    username = models.CharField(max_length=50,unique=True)
    password = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    phone_number = models.CharField(max_length=13)
    user_type = models.CharField(max_length=100, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']
    
    objects = CustomUserManager()
    
    @property
    def assigned_users(self):
        if self.user_type == self.USER_TYPE_COMPANY:
            from tma.models import AdminManage
            user_ids = AdminManage.objects.filter(admin=self).values_list("id", flat=True)
            return CustomUser.objects.filter(id__in=user_ids)
        return CustomUser.objects.none()
        

    def __str__(self):
        return f"{self.name} ({self.username})"

       
class Task(models.Model):
    CHOICES=[
        ('PENDING','pending'),
        ('INPROGRESS','inpogress'),
        ('COMPLETE','complete')
    ]
    title=models.CharField(max_length=50)
    description=models.TextField()
    assigned_to=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    due_date=models.DateField()
    status = models.CharField(max_length=20, choices=CHOICES, default='PENDING')
    completion_report=models.TextField(null=True,blank=True)
    worked_hours=models.IntegerField(null=True,blank=True)
    
    def __str__(self):
        return self.title
    


class AdminManage(models.Model):
    admin=models.ForeignKey(CustomUser,related_name="managed_admins",on_delete=models.CASCADE,limit_choices_to={'user_type': 'ADMIN'})
    user=models.ForeignKey(CustomUser,related_name="managed_users",on_delete=models.CASCADE,limit_choices_to={'user_type': 'USER'})
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['admin', 'user'],
                name='unique_admin_user_pair'
            )
        ]
        
    def __str__(self):
        return f"{self.user.username} assigned to {self.admin.username}"