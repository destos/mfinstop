from django.db.models.query import QuerySet


class ThingQueryset(QuerySet):

    def public_things(self):
        return self.filter(approved=True)

    def good_behavior(self):
        return self.filter(behavior=self.model.GOOD)

    def bad_behavior(self):
        return self.filter(behavior=self.model.BAD)


class MotivePeriodQuerySet(QuerySet):
    pass
