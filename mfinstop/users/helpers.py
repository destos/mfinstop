from allauth.account.utils import user_display
from allauth.socialaccount import providers
from avatar.util import (
    get_default_avatar_url, cache_result, get_user_model, get_user)
from avatar.templatetags.avatar_tags import avatar_url
from avatar.conf import settings as avatar_settings
from django.template import Template, Context
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.translation import ugettext as _
from django.utils import six
import jinja2
from jingo import register, get_env

jinja_env = get_env()


@register.function
def static(path):
    return staticfiles_storage.url(path)


@register.function
@jinja2.contextfunction
def crispy(context, form, helper=None, template_pack='bootstrap', **kwargs):
    mini_template = (
        '{{% load crispy_forms_tags %}}{{% crispy form "{0}" %}}'.format(template_pack))
    t = Template(mini_template)
    context = Context(dict(context))
    context.update({'form': form})
    return t.render(context)


# Avatar template tag converted to use Jinja

@cache_result()
@register.function
def user_avatar(user, size=avatar_settings.AVATAR_DEFAULT_SIZE, **kwargs):
    if not isinstance(user, get_user_model()):
        try:
            user = get_user(user)
            alt = six.text_type(user)
            url = avatar_url(user, size)
        except get_user_model().DoesNotExist:
            url = get_default_avatar_url()
            alt = _("Default Avatar")
    else:
        alt = six.text_type(user)
        url = avatar_url(user, size)
    context = dict(kwargs, **{
        'user': user,
        'url': url,
        'alt': alt,
        'size': size,
    })
    ret = jinja_env.get_template('avatar/avatar_tag.html').render(**context)
    return jinja2.Markup(ret)


# allauth templatetags converted to use Jinja
@register.function
@jinja2.contextfunction
def provider_login_url(context, provider_id, **kwargs):
    provider = providers.registry.by_id(provider_id)
    query = kwargs
    request = context['request']
    if 'next' not in query:
        next = request.REQUEST.get('next')
        if next:
            query['next'] = next
    else:
        if not query['next']:
            del query['next']
    return provider.get_login_url(request, **query)


@register.function
@jinja2.contextfunction
def providers_media_js(context):
    request = context['request']
    ret = '\n'.join([p.media_js(request)
                     for p in providers.registry.get_list()])
    return jinja2.Markup(ret)


@register.function
@jinja2.contextfunction
def do_user_display(context, user):
    display = user_display(user)
    return display
