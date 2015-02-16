import arrow
from django.views.generic import TemplateView

from things.models import Thing, Incident


class HomePageView(TemplateView):
    template_name = 'pages/home.html'
    http_method_names = ['get']
    num_things = 10

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'some_things': self.get_example_community_things(),
            'recent_bad_incidents': self.get_last_24_hours(),
            'recent_good_incidents': self.get_last_24_hours(Thing.GOOD)
        })
        return context

    def get_example_community_things(self):
        """Get random things from the database"""
        return Thing.objects.public_things().order_by('?')[:self.num_things]

    def get_last_24_hours(self, behavior=Thing.BAD):
        now = arrow.utcnow()
        amounts = []
        for hour in arrow.Arrow.range('hour', now.replace(hours=-24), now.ceil('hour')):
            amounts.append(
                Incident.objects.filter(
                    motive__thing__behavior=behavior,
                    created__range=(
                        hour.replace(hours=-1).datetime, hour.datetime)).count())
        return {
            'total': sum(amounts),
            'max': max(amounts),
            'over_24_hours': amounts,
        }



class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class FAQPageView(TemplateView):
    template_name = 'pages/faq.html'


class ContactPageView(TemplateView):
    template_name = 'pages/contact.html'
