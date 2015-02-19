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
        # motives = self.get_active_motives().filter(
        #     periods__ends__range=(
        #         now.replace(day=+1).date(), now.date()))
        motives = self.get_active_motives()
        new_periods = []
        for motive in motives:
            period = motive.current_period
            new_period = None
            if not motive.user.is_active:
                continue
            if period and period.days_left < 0:
                new_period = CreateMotivePeriod().delay(motive, start=arrow.get(period.ends).replace(days=+1))
            elif not period:
                # Task to create new period
                new_period = CreateMotivePeriod().delay(motive, start=now)
            # TODO: Task to send notification of new period
            if new_period:
                new_periods.append(new_period)
        return new_periods


class CreateMotivePeriod(Task):
    ignore_results = True

    def run(self, motive, start=None):
        try:
            period = create_period(motive, start)
        except AssertionError, e:
            print("assertion error when creating new period for motive {},\n{}".format(motive, e))
            return None
        print("Created new period for motive {}".format(motive))
        return period


def run():
    return CheckEndingPeriods().run()
