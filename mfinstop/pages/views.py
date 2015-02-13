from django.views.generic import TemplateView

from things.models import Thing


class HomePageView(TemplateView):
    template_name = 'pages/home.html'
    http_method_names = ['get']
    num_things = 10

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context.update({
            'some_things': self.get_example_community_things()
        })
        return context

    def get_example_community_things(self):
        """Get random things from the database"""
        return Thing.objects.public_things().order_by('?')[:self.num_things]


class AboutPageView(TemplateView):
    template_name = 'pages/about.html'


class FAQPageView(TemplateView):
    template_name = 'pages/faq.html'


class ContactPageView(TemplateView):
    template_name = 'pages/contact.html'
