import arrow
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives
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
        now = arrow.utcnow().ceil('days')
        motives = self.get_active_motives().filter(
            periods__ends__range=(
                now.date(), now.floor('days').date()))
        for motive in motives:
            # calculate time till task needs run.
            morning = now.floor('days').replace(minute=+10)
            CreateMotivePeriod().apply_async(motive, eta=morning.datetime)
        return motives


class CreateMotivePeriod(app.Task):
    ignore_results = True

    def run(self, motive):
        period = create_period(motive)
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


class EmailTask(app.Task):
    """
    """

    ignore_results = True
    email_template = 'emails/text'
    email_subject = 'change me'

    def get_email_context(self, **extra_context):
        context = {}
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


class SendSummaryEmail(EmailTask):
    """
    Sends the user their summary email with links to admit quit.
    """

    email_template = 'emails/summary_email'
    email_subject = 'give us updates'

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
        if force is True or user.motives and not user.quitter:
            self.send_email({'user': user})
