# -*- coding: utf-8 -*-
from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from hijack.admin import HijackUserAdminMixin

from .models import User


class MyUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class MyUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class UserAdmin(
        AuthUserAdmin,
        HijackUserAdminMixin):
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = (
        'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff',
        'is_superuser', 'hijack_field')


admin.site.register(User, UserAdmin)
