from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.models import TimeStampModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError("올바른 이메일을 입력해주세요.")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            nickname=nickname,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password=None):
        user = self.create_user(email, nickname, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(TimeStampModel, AbstractBaseUser, PermissionsMixin):

    class Gender(models.TextChoices):
        MALE = "M", "남"
        FEMALE = "F", "여"

    class Job(models.TextChoices):
        EMPLOYEE = "EMPLOYEE", "직장인"
        STUDENT = "STUDENT", "학생"
        FREELANCER = "FREELANCER", "프리랜서"
        HOUSEWIFE = "HOUSEWIFE", "주부"
        OTHER = "OTHER", "기타"

    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=20, unique=True)

    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    job = models.CharField(max_length=20, choices=Job.choices, blank=True, null=True)

    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "유저"
        verbose_name_plural = f"{verbose_name} 목록"

    def __str__(self):
        return self.email