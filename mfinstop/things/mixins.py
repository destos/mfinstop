from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import redirect_to_login
from django.http import Http404
from django.shortcuts import get_object_or_404

from .models import UserMotive


class UserMotiveMixin(object):

    motive = False
    motive_model = UserMotive
    motive_pk_url_kwarg = 'motive_pk'
    motive_slug_url_kwarg = 'motive_slug'

    def dispatch(self, request, *args, **kwargs):
        self.motive_pk = int(kwargs.get(self.motive_pk_url_kwarg, None))
        self.motive_slug = str(kwargs.get(self.motive_slug_url_kwarg, None))
        return super(UserMotiveMixin, self).dispatch(request, *args, **kwargs)

    def get_motive(self):
        if self.motive:
            return self.motive
        if hasattr(self, 'motive_pk'):
            self.motive = get_object_or_404(self.motive_model, id=self.motive_pk)
        elif hasattr(self, 'motive_slug'):
            self.motive = get_object_or_404(self.motive_model, serial_number=self.motive_slug)
        else:
            raise Http404
        return self.motive

    def get_context_data(self, **kwargs):
        context = super(UserMotiveMixin, self).get_context_data(**kwargs)
        context.update({
            'motive_pk': self.motive_pk or self.motive.id,
            'motive': self.motive
        })
        return context


class UserMotiveObjectMixin(UserMotiveMixin):
    def get_object(self, *args, **kwargs):
        return self.get_motive(*args, **kwargs)


class UserMotiveFormKwargsMixin(object):
        def get_form_kwargs(self):
            """Pass in motive"""
            kwargs = super(UserMotiveFormKwargsMixin, self).get_form_kwargs()
            kwargs.update({'motive': self.get_motive()})
            return kwargs


class UserMotiveAccess(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        assert hasattr(self, 'get_motive')
        if self.get_motive().user == request.user and not (
                request.user.is_superuser):
            if self.raise_exception:
                raise PermissionDenied  # return a forbidden response
            else:
                return redirect_to_login(request.get_full_path(),
                                         self.get_login_url(),
                                         self.get_redirect_field_name())
        response = super(UserMotiveAccess, self).dispatch(
            request, *args, **kwargs)
        return response
