from django.conf import settings


def google_ua(request):
    return {'google_ua': settings.GOOGLE_TRACKING_ID}
