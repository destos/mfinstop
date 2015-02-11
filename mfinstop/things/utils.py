import arrow
from .models import MotivePeriod, UserMotive


def create_period(motive, start=None):
    if start is None:
        start = arrow.utcnow()
    # import ipdb; ipdb.set_trace()
    assert isinstance(start, arrow.Arrow)
    assert isinstance(motive, UserMotive)
    end = start.replace(seconds=+motive.duration.total_seconds())
    # Check that an overlapping period doesn't already exist
    assert not motive.periods.filter(ends__gt=start.date).exists()
    return MotivePeriod.objects.create(
        motive=motive, starts=start.date(), ends=end.date())
