# -*- coding: utf-8 -*-
# from __future__ import absolute_import
from allauth.account.forms import LoginForm as AALoginForm
from django import forms

from misc.forms import CrispyFormMixin
from .models import User


class UserForm(forms.ModelForm):

    class Meta:
        # Set this form to use the User model.
        model = User

        # Constrain the UserForm to just these fields.
        fields = ("first_name", "last_name")


# Forms for allauth customizations

class LoginForm(CrispyFormMixin, AALoginForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper.form_tag = False
