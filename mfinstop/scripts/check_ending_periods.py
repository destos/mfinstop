import arrow

from . import Task, ActiveMotiveTaskMixin
from things.utils import create_period


class CheckEndingPeriods(
        ActiveMotiveTaskMixin,
        Task):
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


class CreateMotivePeriod(Task):
    ignore_results = True

    def run(self, motive, eta):
        period = create_period(motive, start=eta)
        print("Created new period for motive {}".format(motive))
        return period


def run():
    return CheckEndingPeriods().run()
