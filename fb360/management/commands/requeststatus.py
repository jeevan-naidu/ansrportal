from django.core.management.base import BaseCommand

import fb360

from datetime import date

from django.contrib.auth.models import User

from templated_email import send_templated_mail

from django.conf import settings


class Command(BaseCommand):
    help = 'To send the status of requests and un raised requesting persons name'

    def handle(self, *args, **options):
        data = {}
        data['pending_count'] = get_status_queryset(status=fb360.models.STATUS[0][0]).count()
        data['approved_count'] = get_status_queryset(status=fb360.models.STATUS[1][0]).count()
        data['rejected_count'] = get_status_queryset(status=fb360.models.STATUS[2][0]).count()

        this_year_fb = fb360.models.FB360.objects.filter(
            start_date__year=date.today().year).values('eligible').distinct()

        if len(this_year_fb):
            this_year_fb_eligible_ids = [eachRec['eligible'] for eachRec in this_year_fb]

            if len(this_year_fb_eligible_ids):
                resp = fb360.models.Respondent.objects.filter(
                    initiator__survey__start_date__year=date.today().year
                ).values('employee').distinct()
                init = fb360.models.Initiator.objects.filter(
                    survey__start_date__year=date.today().year
                ).values('employee').distinct()
                initiated_ids = set([eachRec['employee'] for eachRec in resp] + [eachRec['employee'] for eachRec in init])
                yet_to_start_members = set(this_year_fb_eligible_ids) - initiated_ids

                l = []
                for eachRec in list(yet_to_start_members):
                    user_obj = User.objects.get(id=eachRec)
                    l.append('{0} {1}'.format(user_obj.first_name, user_obj.last_name))
                data['still_to_start'] = l
        send_email(self, data)


def get_status_queryset(**kwargs):
    return fb360.models.Respondent.objects.filter(**kwargs)


def send_email(self, data):
    if len(data) > 0:
        send_templated_mail(
            template_name='FB360StatusNotification',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=settings.EMAIL_ABOUT_STATUS,
            context={'data': data}
        )