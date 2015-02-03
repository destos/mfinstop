from betterforms.multiform import MultiModelForm
from braces.forms import UserKwargModelFormMixin
from django import forms

from .models import UserMotive, Thing


class CreateUserMotiveForm(
        UserKwargModelFormMixin,
        forms.ModelForm):

    duration = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '7 days',
        'class': 'form-control input-lg'
    }))

    def __init__(self, *args, **kwargs):
        ret = super(CreateUserMotiveForm, self).__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs = {'class': 'form-control input-lg'}
        return ret

    class Meta:
        model = UserMotive
        fields = ('amount', 'duration',)

    def save(self, commit=True):
        object = super(CreateUserMotiveForm, self).save(commit=False)
        object.user = self.user
        if commit:
            object.save()
        return object


class ThingForm(
        UserKwargModelFormMixin,
        forms.ModelForm):

    name = forms.CharField(widget=forms.TextInput(attrs={
        # 'verbose_name': 'Thing name',
        'placeholder': 'Chinease Food',
        'class': 'form-control input-lg'
    }))

    # behavior = forms.ChoiceField(widget=forms.Select(attrs={
    #     'class': 'form-control'
    # }))

    verb = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'eating',
        'class': 'form-control input-lg'
    }))

    def __init__(self, *args, **kwargs):
        ret = super(ThingForm, self).__init__(*args, **kwargs)
        self.fields['behavior'].widget.attrs = {'class': 'form-control input-lg'}
        return ret

    class Meta:
        model = Thing
        fields = ('name', 'behavior', 'verb',)

    def clean(self):
        """Don't check for uniqueness, save just returns the existing object"""
        pass

    def save(self, commit=True):
        try:
            return Thing.objects.get(**self.cleaned_data)
        except Thing.DoesNotExist:
            object = super(ThingForm, self).save(commit=commit)
            object.creator = self.user
            if commit:
                object.save()
            return object


class CreateThingAndUserMotiveForm(MultiModelForm):
    form_classes = {
        'motive': CreateUserMotiveForm,
        'thing': ThingForm,
    }

    # may need to change to form_valid for validation?
    def save(self, commit=True):
        objects = super(CreateThingAndUserMotiveForm, self).save(commit=False)
        if commit:
            # Save in correct order
            objects['thing'].save()
            objects['motive'].thing = objects['thing']
            objects['motive'].save()
        return objects
