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
    The details of the thing the user is trying to accomplish
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


class MotivePeriod(models.Model):
    """
    The period over which one is attempting to meet/limit their motive amount
    """
    motive = models.ForeignKey(UserMotive, related_name='periods')
    starts = models.DateField()
    ends = models.DateField()

    objects = MotivePeriodQuerySet.as_manager()

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
