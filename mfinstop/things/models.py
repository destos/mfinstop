import arrow
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django_extensions.db.fields import AutoSlugField
from durationfield.db.models.fields.duration import DurationField

from users.models import User
from .querysets import ThingQueryset, MotivePeriodQuerySet


class Thing(TimeStampedModel):
    """
    A thing one would like to do less or more of.
    """
    name = models.CharField(db_index=True, max_length=255)
    slug = AutoSlugField(
        db_index=True, max_length=255, populate_from='name', allow_duplicates=False)

    BAD = 0
    GOOD = 1
    BEHAVIOR_CHOICES = (
        (GOOD, 'start'),
        (BAD, 'stop')
    )
    # Could use a boolean field? if we want to store different behaviors, maybe not.
    behavior = models.PositiveSmallIntegerField(choices=BEHAVIOR_CHOICES, default=BAD)
    verb = models.CharField(db_index=True, max_length=255, blank=True, null=True)

    # The user that created this thing, and whether or not it should be public
    creator = models.ForeignKey(User, blank=True, null=True)
    approved = models.BooleanField(default=False)

    objects = ThingQueryset.as_manager()

    class Meta:
        ordering = ('-created',)
        # allows for multiple verbs with the same thing name,
        # and a thing to be both good and bad
        # unique_together = (
        #     ('name', 'verb'),
        #     ('name', 'behavior'),
        # )

    def __unicode__(self):
        return "{} {} {}".format(self.get_behavior_display(), self.verb, self.name)


class UserMotive(TimeStampedModel):
    """
    The details of the thing the user is trying to accomplish,
    You can't quit individual motives, a user must deactivate their account
    by becoming a quitter.
    """
    user = models.ForeignKey(User, related_name='motives')
    thing = models.ForeignKey(Thing)
    # The goal amount to limit by or reach depending on if this is a good/bad thing
    amount = models.PositiveSmallIntegerField(default=1)
    duration = DurationField()

    class Meta:
        unique_together = ('user', 'thing')

    def __unicode__(self):
        return "{}, {} - {}, every {}".format(self.user, self.thing, self.amount, self.duration)

    @models.permalink
    def get_detail_url(self):
        return ('things:motive_detail', (), {'motive_pk': self.pk})

    @property
    def latest_period(self):
        try:
            return self.periods.latest()
        except MotivePeriod.DoesNotExist:
            return None

    def create_incident(self):
        return Incident.objects.create(motive=self)


class MotivePeriod(models.Model):
    """
    The period over which one is attempting to meet/limit their motive amount
    """
    motive = models.ForeignKey(UserMotive, related_name='periods')
    starts = models.DateField()
    ends = models.DateField()

    objects = MotivePeriodQuerySet.as_manager()

    def __unicode__(self):
        return "{} days left, {} incidents".format(self.days_left, len(self.incidents))

    @property
    def incidents(self):
        """
        Get a filterd range of incidents that occured in this motive period
        """
        return self.motive.incidents.filter(
            created__range=(self.starts, self.ends))

    @property
    def fill_ratio(self):
        incidents = self.incidents
        if incidents:
            return float(len(incidents)) / float(self.motive.amount)
        return float(0)

    @property
    def incidents_left(self):
        return max(self.motive.amount - len(self.incidents), 0)

    @property
    def length(self):
        return (self.ends - self.starts).days

    @property
    def days_left(self):
        present = arrow.utcnow()
        return (arrow.get(self.ends) - present).days

    @property
    def days_left_display(self):
        return arrow.get(self.ends).humanize()

    @property
    def past_today(self):
        present = arrow.utcnow()
        return present.date() > self.ends

    @property
    def days_past(self):
        return self.length - self.days_left

    @property
    def progress_bars(self):
        """
        Context for progress bar rendering
        info bar shows days as they pass, primary color bar fills up incidents to total,
        If the total moves past the day percent it turns the warning colors,
        if it moves past the motive amount limit it turns the danger color.
        """
        total_days = self.length
        days_past = self.days_past
        incident_day_ratio = float(total_days) / float(self.motive.amount)
        max_incidents = float(self.motive.amount) * incident_day_ratio

        incidents = self.incidents
        incidents_amount = len(incidents)
        current_incidents = incidents_amount * incident_day_ratio

        # TODO: indicator for open days shows how many days left

        # Determine the highest increment
        if current_incidents > total_days:
            # If the incidents are already more than days that can pass we wont
            # be showing any days
            max_amount = current_incidents
        else:
            max_amount = float(total_days)

        bars = []

        def make_percent(amount=0):
            return (float(amount) / max_amount) * 100

        good_band = min(current_incidents, days_past)
        bars.append({
            # Incidents that haven't past the days_past amount
            'name': 'good_incidents',
            'type': 'primary',
            'percent': make_percent(good_band),
            'indi': 'within bounds',
        })

        over_incidents = max(current_incidents - max_incidents, 0)
        if current_incidents > days_past:
            # incidents that occur past the date percent, (going on a negative incident rate)
            bars.append({
                'name': 'warning_incidents',
                'type': 'warning',
                'percent': make_percent(min(current_incidents, total_days)),
                'indi': 'over safe zone',
            })

        elif current_incidents < days_past:
            bars.append({
                'name': 'days_past',
                'type': 'info',
                'percent': make_percent(days_past),
                'indi': 'safe zone'
            })

        if bool(over_incidents):
            over_bar = make_percent(current_incidents)
            # incidents that pass the max_incidents
            over_by = incidents_amount - self.motive.amount
            if self.motive.thing.behavior == Thing.GOOD:
                bars.append({
                    'name': 'good_incidents_over',
                    'type': 'success',
                    'percent': over_bar,
                    'text': "{} more!".format(over_by),
                    'indi': "over limit, but good."
                })
            else:
                bars.append({
                    'name': 'bad_incidents',
                    'type': 'danger',
                    'percent': over_bar,
                    'text': "{} over!".format(over_by),
                    'indi': 'over limit, tsk tsk!'
                })

        returned_bars = []
        for i, bar in enumerate(bars):
            right = i - len(bars)
            previous_bars = list(bars)[:right]
            prev_percents = sum([pbar['percent'] for pbar in previous_bars])
            # remove previous bar space from this bar
            bar['percent'] -= prev_percents
            if bar['percent'] <= 0:
                continue
            returned_bars.append(bar)
        return bars

    class Meta:
        get_latest_by = ('starts')


class Incident(TimeStampedModel):
    """
    A record of a thing incident
    eg. Patrick ate a cookie
    """
    motive = models.ForeignKey(UserMotive, related_name='incidents')

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return "{} - incident".format(self.motive)
