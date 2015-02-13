from . import Task, ActiveMotiveTaskMixin

from users.models import User
from .send_summary_email import SendSummaryEmail


class SendDailyEmails(
        ActiveMotiveTaskMixin,
        Task):
    """
    Looks through all motives where a user is not a quitter and queues up emails
    to check for any incidents by those users.
    """

    def run(self):
        active_users = User.objects.filter(quitter=False)
        for user in active_users:
            # TODO: check contact preference, SMS, email ect.
            SendSummaryEmail().delay(user)


def run():
    SendDailyEmails().run()
