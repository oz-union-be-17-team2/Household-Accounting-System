from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from household_budget.core.models import TimeStampModel


class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, nickname, phone_number, password=None):
        if not email:
            raise ValueError("올바른 이메일을 입력해주세요.")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            nickname=nickname,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, nickname, phone_number, password=None):
        user = self.create_user(email, name, nickname, phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(TimeStampModel, AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=20)
    nickname = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)

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
