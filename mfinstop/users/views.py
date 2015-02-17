# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
from django.contrib.contenttypes.models import ContentType
from braces.views import LoginRequiredMixin

from .forms import UserForm
from .models import User
from things.models import Thing


class UserDetailView(
        LoginRequiredMixin,
        DetailView):
    model = User
    context_object_name = 'user_details'

    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context.update({
            'get_user_actions': self.get_user_actions
        })
        return context

    def get_user_actions(self):
        return self.object.actions.exclude(
            content_type=ContentType.objects.get_for_model(Thing))


class UserRedirectView(
        LoginRequiredMixin,
        RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})


class UserUpdateView(
        LoginRequiredMixin,
        UpdateView):

    form_class = UserForm

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse("users:detail",
                       kwargs={"username": self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(
        LoginRequiredMixin,
        ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = "username"
    slug_url_kwarg = "username"
