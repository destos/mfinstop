# -*- coding: utf-8 -*-
# Import the AbstractUser model
from django.contrib.auth.models import AbstractUser
from allauth.account.models import EmailAddress

# Import the basic Django ORM models library
from django.db import models

from django.utils.translation import ugettext_lazy as _


# Subclass AbstractUser
class User(AbstractUser):

    quitter = models.BooleanField(default=False)

    def __unicode__(self):
        return self.username

    @property
    def prefered_email(self):
        try:
            return self.emailaddress_set.get(primary=True).email
        except EmailAddress.DoesNotExist:
            return self.email

    @property
    def email_to_header(self):
        return "{} <{}>".format(self.get_full_name(), self.prefered_email)
