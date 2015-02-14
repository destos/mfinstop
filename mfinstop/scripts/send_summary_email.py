from . import EmailTask
from users.models import User


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
        if not isinstance(user, User):
            user = User.objects.get(id=int(user))
        if not force and not user.is_active:
            return
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


def run(user_id, force=False):
    SendSummaryEmail().run(user_id, force)
