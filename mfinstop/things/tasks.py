import arrow
from celery.utils.log import get_task_logger

from celery_tasks import app
from .models import UserMotive
from .utils import create_period


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

