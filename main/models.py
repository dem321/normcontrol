from typing import Optional
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.apps import apps

class CustomUserManager(BaseUserManager):

    def _create_user(self, username, person_id, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not username:
            raise ValueError("The given username must be set")
        GlobalUserModel = apps.get_model(
            self.model._meta.app_label, self.model._meta.object_name
        )
        username = GlobalUserModel.normalize_username(username)
        user = self.model(username=username, person_id=person_id, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, username, person_id=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, person_id, password, **extra_fields)

    def create_superuser(self, username, person_id=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, person_id, password, **extra_fields)


class Department(models.Model):
    """Справочник подразделений""" 
    name = models.CharField(max_length=3)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)

class Site(models.Model):
    """Справочник соотношения участок на подразделениях"""
    site = models.CharField(max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class Person(models.Model):
    """Справочник сотрудников предприятия"""
    first_name = models.CharField('Имя', max_length=15)
    second_name = models.CharField('Фамилия', max_length=15)
    middle_name = models.CharField('Отчество', max_length=15)
    email = models.EmailField('Email', blank=True, null=True)
    occupation = models.CharField('Должность', max_length=100)
    tab_num = models.IntegerField('Табельный номер')
    department = models.ForeignKey(Department,verbose_name='Подразделение', on_delete=models.CASCADE)
    site = models.ForeignKey(Site, verbose_name='Участок', blank=True, null=True, on_delete=models.CASCADE)

class PhoneNumber(models.Model):
    phone = models.CharField('Номер телефона', max_length=5)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

class User(AbstractBaseUser, PermissionsMixin):

    password = models.CharField(_("password"), max_length=128, blank=True, null=True, default='')
    username = models.CharField(_("username"), max_length=150, unique=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)  
    person = models.ForeignKey(Person, null=True, blank=True, on_delete=models.PROTECT)

    objects = CustomUserManager()
 
    USERNAME_FIELD = "username"

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

class PersonToUser(models.Model):
    """Справочник соотношения сотрудника к имени его пользователя"""
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    username = models.CharField('Имя пользователя', max_length=100)

class Action(models.Model):
    action_type = models.CharField('Тип действия', max_length=50)

    def __str__(self):
        return self.action_type

class DocumnetType(models.Model):
    document_type = models.CharField('Вид документа', max_length=20)

    def __str__(self):
        return self.document_type
    
class Document(models.Model):
    name = models.CharField('Обозначение документа', max_length=100)
    list_count_document = models.IntegerField('Количество листов документа')
    notice_name = models.CharField('Обозначение извещения', max_length=100, null=True, blank=True)
    list_count_notice = models.IntegerField('Количество листов извещения', null=True, blank=True)
    creation_date = models.DateField('Дата создания', auto_now_add=True)
    creator = models.ForeignKey(Person, models.CASCADE, verbose_name='Исполнитель документа')
    type = models.ForeignKey(DocumnetType, models.PROTECT, verbose_name='Вид документа')
    phone = models.CharField('Номер телефона исполнителя', max_length=5, null=True, blank=True)

    def __str__(self):
        return self.name
    
class ActionOnDocument(models.Model):
    action_date = models.DateTimeField('Дата действия', auto_now_add=True)
    comment = models.CharField('Комментарий', max_length=100, default='')
    action = models.ForeignKey(Action, models.PROTECT, verbose_name='Действие с документом')
    user = models.ForeignKey(User, models.CASCADE, verbose_name='Пользователь совершивший действие')
    doc = models.ForeignKey(Document, models.CASCADE, verbose_name='Документ')

    def __str__(self):
        return self.action_date+' '+str(self.doc)

    
