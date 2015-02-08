from braces.views import (
    LoginRequiredMixin, UserFormKwargsMixin, FormMessagesMixin,
    SuccessURLRedirectListMixin, UserPassesTestMixin)
from django.views.generic import DetailView, UpdateView, ListView, CreateView
from django.views.generic.edit import BaseCreateView

from . import forms
from . import models
from . import utils
from . import mixins


# A view where users can create their motives
class MotiveCreateView(
        LoginRequiredMixin,
        UserFormKwargsMixin,
        FormMessagesMixin,
        SuccessURLRedirectListMixin,
        CreateView):

    """
    Create a User motive
    """

    form_invalid_message = "That didn't work, it's obviously your fault."
    form_valid_message = "We've got it, now get your act together."
    success_list_url = 'things:motives_list'

    template_name = 'things/create_motive.html'
    form_class = forms.CreateThingAndUserMotiveForm

    def form_valid(self, form):
        response = super(MotiveCreateView, self).form_valid(form)
        # Starting Period for
        utils.create_period(form['motive'].instance)
        return response


# TODO: Edit their motives

# TODO?: Delete their motives

class MotiveListView(
        LoginRequiredMixin,
        ListView):

    """
    List all a users motives
    """

    template_name = 'things/motive_list.html'
    context_object_name = 'motive_list'

    def get_queryset(self):
        return models.UserMotive.objects.filter(user=self.request.user)


class MotiveIncidentView(
        mixins.UserMotiveMixin,
        mixins.UserMotiveFormKwargsMixin,
        mixins.UserMotiveAccess,
        SuccessURLRedirectListMixin,
        FormMessagesMixin,
        BaseCreateView):

    """
    Log an incident to a user's motive,
    Prevent from creating a new incident if the last one is less than an hour old
    """

    http_method_names = ('post',)
    success_list_url = 'things:motives_list'
    model = models.Incident
    motive_pk_url_kwarg = 'motive_pk'
    form_class = forms.CreateIncidentForm

    def get_thing_sentiment(self):
        return 'good' if self.object.motive.thing.behavior is models.Thing.GOOD else 'bad'

    def get_form_valid_message(self):
        messages = {
            'good': 'Good on ya, keep it up.',
            'bad': 'Logged, thanks for admitting guilt.'
        }
        return messages[self.get_thing_sentiment()]

    def get_form_invalid_message(self):
        messages = {
            'good': 'Wasn\'t able log that sorry.',
            'bad': 'Gona have to wait a bit before you can commit that atrocity again.'
        }
        return messages[self.get_thing_sentiment()]

    def form_invalid(self, form):
        return self.form_valid(form)


# View their motive's details and the incidents.
class MotiveDetailView(
        LoginRequiredMixin,
        DetailView):

    pk_url_kwarg = 'motive_pk'

    template_name = 'thing/motive_detail.html'
    context_object_name = 'motive'
