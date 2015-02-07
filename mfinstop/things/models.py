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
    user = models.ForeignKey(User)
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
        return self.days_left

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
        incidents = self.incidents
        max_incidents = self.motive.amount
        current_incidents = len(incidents)
        total_days = self.length
        days_past = self.days_past
        # Determine the highest increment
        if current_incidents > total_days:
            # If the incidents are already more than days that can pass we wont
            # be showing any days
            max_amount = current_incidents
        else:
            max_amount = total_days

        bars = []

        def make_percent(amount=0):
            return (float(amount) / float(max_amount)) * 100

        good_band = min(current_incidents, days_past)
        bars.append({
            # Incidents that haven't past the days_past amount
            'name': 'good_incidents',
            'type': 'primary',
            'percent': make_percent(good_band)
        })

        warning_band = 0
        over_incidents = max(current_incidents - max_incidents, 0)
        if current_incidents > days_past:
            # incidents that occur past the date percent, (going on a negative incident rate)
            warning_band = (current_incidents - good_band - over_incidents)
            bars.append({
                'name': 'warning_incidents',
                'type': 'warning',
                'percent': make_percent(warning_band)
            })

        elif current_incidents < days_past:
            bars.append({
                'name': 'days_past',
                'type': 'info',
                'percent': make_percent(days_past - (current_incidents))
            })

        if bool(over_incidents):
            # incidents that pass the max_incidents
            bars.append({
                'name': 'bad_incidents',
                'type': 'danger',
                'percent': make_percent(over_incidents),
                'text': "{} over!".format(over_incidents)
            })

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
