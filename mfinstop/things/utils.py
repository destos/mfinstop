import arrow
from .models import MotivePeriod, UserMotive


def create_period(motive, start=None):
    if start is None:
        start = arrow.utcnow()
    assert isinstance(start, arrow.Arrow)
    assert isinstance(motive, UserMotive)
    end = start.replace(seconds=+motive.duration.total_seconds())
    # Check that an overlapping period doesn't already exist
    assert not motive.periods.filter(ends__lt=start.datetime).exists()
    return MotivePeriod.objects.create(
        motive=motive, starts=start.datetime, ends=end.datetime)
