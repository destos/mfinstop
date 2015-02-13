import arrow
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
from jingo import get_env

from celery_tasks import app
from users.models import User
from .models import UserMotive
from .utils import create_period


jinja_env = get_env()


logger = get_task_logger(__name__)


class ActiveMotiveTaskMixin(object):
    """Allows tasks to retrieve currently active motives"""

    def get_active_motives(self):
        return UserMotive.objects.filter(user__quitter=False)


class CheckEndingPeriods(
        ActiveMotiveTaskMixin,
        app.Task):
    """
    A daily task that checks for motives that are ending and schedules a motive
    period to be created at the exact time it's needed.
    """

    def run(self):
        now = arrow.utcnow().ceil('day')
        motives = self.get_active_motives().filter(
            periods__ends__range=(
                now.date(), now.floor('day').date()))
        for motive in motives:
            # calculate time till task needs run.
            morning = now.floor('day').replace(minute=+10)
            # Task to create new period
            CreateMotivePeriod().apply_async(motive, eta=morning.datetime)
            # TODO: Task to send notification of new period
        return motives


class CreateMotivePeriod(app.Task):
    ignore_results = True

    def run(self, motive, eta):
        period = create_period(motive, start=eta)
        logger("Created new period for motive {}".format(motive))
        return period


class SendDailyEmails(
        ActiveMotiveTaskMixin,
        app.Task):
    """
    Looks through all motives where a user is not a quitter and queues up emails
    to check for any incidents by those users.
    """

    def run(self):
        active_users = User.objects.filter(quitter=False)
        for user in active_users:
            # TODO: check contact preference, SMS, email ect.
            SendSummaryEmail().delay(user)


class CheckForEmptyMotives(app.Task):
    """
    Check for users that have not created any motives and send them an introductory email.
    make sure now to spam the user, so log that the email was sent and only send it
    every month?
    """
    pass


class EmailTask(app.Task):
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


class SendSummaryEmail(EmailTask):
    """
    Sends the user their summary email with links to admit quit.
    """

    email_template = 'emails/summary_email'
    email_subject = 'What have you been up to?'

    def get_metadata(self, **context):
        meta = super(SendSummaryEmail, self).get_metadata()
        user = context.get('user', None)
        if user:
            meta.update({'user_id': user.pk})
            return meta
        else:
            return meta

    def get_recipients(self, **context):
        return [context.get('user').email_to_header]

    def run(self, user, force=False):
        motives = user.motives.all()
        if force is True or (motives and not user.quitter):
            pos_motives = motives.good_motives()
            neg_motives = motives.good_motives()
            context = {
                'user': user,
                'motives': motives,
                'has_positive_motive': bool(pos_motives),
                'has_negative_motive': bool(neg_motives),
                'positive_motives': pos_motives,
                'negative_motives': neg_motives,
                'num_motives': len(motives),
            }
            self.send_email(context)
