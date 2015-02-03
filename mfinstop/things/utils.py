import arrow
from .models import MotivePeriod


def create_period(motive):
    start = arrow.utcnow()
    end = start.replace(seconds=+motive.duration.total_seconds())
    return MotivePeriod.objects.create(
        motive=motive, starts=start.datetime, ends=end.datetime)
