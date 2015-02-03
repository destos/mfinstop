from braces.views import (
    LoginRequiredMixin, UserFormKwargsMixin, FormMessagesMixin,
    SuccessURLRedirectListMixin)
from django.views.generic import DetailView, UpdateView, ListView, CreateView

from . import forms
from . import models
from . import utils


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


# Edit their motives

# Delete their motives

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
        LoginRequiredMixin,
        # UserFormKwargsMixin,
        FormMessagesMixin,
        CreateView):

    """
    Log an incident their motive
    """

    template_name = ''
    model = models.Incident


# View their motive's details and the incidents.
class MotiveDetailView(
        LoginRequiredMixin,
        DetailView):

    pk_url_kwarg = 'motive_pk'

    template_name = 'thing/motive_detail.html'
    context_object_name = 'motive'
