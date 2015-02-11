from django.template.loader import render_to_string
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions as BSFormActions
from crispy_forms.utils import render_field, TEMPLATE_PACK


DEFAULT_LABEL_COL = 3
DEFAULT_FIELD_COL = 9


class CrispyFormMixin(object):
    """
    Small helper that instantiates the crispy FormHelper attribute on any form
    with styling used on the FLA portal forms.
    """
    def __init__(self, *args, **kwargs):
        cols = kwargs.pop('cols', None)
        if cols:
            kwargs.update({
                'label_col': cols[0],
                'field_col': cols[1]
            })
        self.helper = FormHelper()
        self.helper.disable_csrf = False
        self.helper.html5_required = True  # render required attribute
        self.helper.form_class = 'form-horizontal'
        self.helper.cols = {
            'label_col': kwargs.pop('label_col', DEFAULT_LABEL_COL),
            'field_col': kwargs.pop('field_col', DEFAULT_FIELD_COL),
        }
        self.helper.label_class = 'col-md-{label_col}'.format(**self.helper.cols)
        self.helper.field_class = 'col-md-{field_col}'.format(**self.helper.cols)
        super(CrispyFormMixin, self).__init__(*args, **kwargs)


class FormActions(BSFormActions):
    """
    Bootstrap layout object. It wraps fields in a <div class="form-group">
    Also uses the helpers col settings to offset buttons correctly.
    Example::
        FormActions(
            HTML(<span style="display: hidden;">Information Saved</span>),
            Submit('Save', 'Save', css_class='btn-primary'), cols=self.helper.cols)
    """

    template = 'bootstrap3_fla/layout/formactions.jinja'

    def __init__(self, *fields, **kwargs):
        self.fields = list(fields)
        self.template = kwargs.pop('template', self.template)
        self.cols = kwargs.pop('cols', {
            'label_col': DEFAULT_LABEL_COL,
            'field_col': DEFAULT_FIELD_COL})
        self.attrs = kwargs
        if 'css_class' in self.attrs:
            self.attrs['class'] = self.attrs.pop('css_class')

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        html = u''
        for field in self.fields:
            html += render_field(field, form, form_style, context, template_pack=template_pack, **kwargs)
        extra_context = {
            'formactions': self,
            'fields_output': html,
        }
        extra_context.update(self.cols)
        return render_to_string(self.template, extra_context, context)
