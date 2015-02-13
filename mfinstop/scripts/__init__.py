from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from jingo import get_env

from things.models import UserMotive


jinja_env = get_env()


class ActiveMotiveTaskMixin(object):
    """Allows tasks to retrieve currently active motives"""

    def get_active_motives(self):
        return UserMotive.objects.filter(user__quitter=False)


class Task(object):
    """Mimics celery tasks to we can swap to them if needed in the future"""
    def run(self, *args, **kwargs):
        raise NotImplementedError

    def delay(self, *args, **kwargs):
        return self.run(*args, **kwargs)


class EmailTask(Task):
    """
    """

    ignore_results = True
    email_template = 'emails/text'
    email_subject = 'change me'

    def get_email_context(self, **extra_context):
        context = {
            'site': self.get_site()
        }
        context.update(extra_context)
        return context

    def render_email(self, **context):
        context = self.get_email_context(**context)
        rendered = []
        for alt in ('html', 'txt'):
            rendered.append(
                jinja_env.get_template("{}.{}".format(
                    self.email_template, alt)).render(**context))
        return rendered

    def send_email(self, context={}):
        (html_email, txt_email) = self.render_email(**context)

        msg = EmailMultiAlternatives(
            subject=self.email_subject,
            body=txt_email,
            to=self.get_recipients(**context),
        )
        msg.attach_alternative(html_email, "text/html")

        msg.tags = self.get_tags(**context)

        msg.metadata = self.get_metadata(**context)

        msg.send()

    def get_recipients(self, **context):
        """
        eg.
        return ["Recipient One <someone@example.com>", "another.person@example.com"]
        """
        raise NotImplementedError

    def get_metadata(self, **context):
        return {}

    def get_tags(self, **context):
        return []

    def get_site(self):
        if Site._meta.installed:
            return Site.objects.get_current()
        raise ImproperlyConfigured('Site needs defined for email template links')
