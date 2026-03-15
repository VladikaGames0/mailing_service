from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


class User(AbstractUser):
    username = None  # Убираем поле username
    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='users/', null=True, blank=True, verbose_name='Аватар')
    phone = models.CharField(max_length=35, null=True, blank=True, verbose_name='Телефон')
    country = models.CharField(max_length=50, null=True, blank=True, verbose_name='Страна')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email