import arrow
from braces.views import (
    LoginRequiredMixin, UserFormKwargsMixin, FormMessagesMixin,
    SuccessURLRedirectListMixin, UserPassesTestMixin, MessageMixin)
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, UpdateView, ListView, CreateView, View
from django.views.generic.edit import BaseCreateView
import waffle

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


# TODO: put in a limiter that only allows an incident to be posted every hour.
# notify the user that the incident wasn't increased.
class MotiveIncidentView(
        mixins.UserMotiveMixin,
        mixins.UserMotiveAccess,
        SuccessURLRedirectListMixin,
        MessageMixin,
        View):

    """
    Log an incident to a user's motive,
    Prevent from creating a new incident if the last one is less than an hour old
    """

    http_method_names = ('post', 'get',)
    success_list_url = 'things:motives_list'

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        motive = self.get_motive()
        if waffle.flag_is_active(request, 'limit_incident_logging_hourly'):
            hour_ago = arrow.utcnow().replace(hours=-1)
            try:
                latest_incident = motive.incidents.filter(
                    created__gte=hour_ago.datetime).latest()
                # found latest incident
                if latest_incident:
                    self.messages.error(self.get_incident_limit_message(),
                                        fail_silently=True)
                    return HttpResponseRedirect(self.get_success_url())
            except models.Incident.DoesNotExist:
                pass
            incident = models.Incident.objects.create(motive=motive)
            if incident:
                self.messages.success(self.get_form_valid_message(),
                                    fail_silently=True)
        return HttpResponseRedirect(self.get_success_url())

    def get_thing_sentiment(self):
        return 'good' if not self.motive.thing.is_negative else 'bad'

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

    def get_incident_limit_message(self):
        return ("You've reported an incident of {verb} {name} recently. "
                "Please wait a while before reporting again, gosh.".format(
                    verb=self.motive.thing.verb, name=self.motive.thing.name))


# View their motive's details and the incidents.
class MotiveDetailView(
        LoginRequiredMixin,
        DetailView):

    pk_url_kwarg = 'motive_pk'

    template_name = 'thing/motive_detail.html'
    context_object_name = 'motive'
