from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from things.tasks import SendSummaryEmail


User = get_user_model()


class Command(BaseCommand):
    args = '<user_id user_id ...> force=true'
    help = 'Send a user\'s  daily summary emails'

    def handle(self, *args, **options):
        force_send = options.get('force', False)
        for user_id in args:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                raise CommandError('User id {} does not exist'.format(user_id))
            SendSummaryEmail().run(user, force=force_send)
            self.stdout.write("sending summary email to {}".format(user))
