from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings

from templated_email import send_templated_mail


def email_new_user(sender, **kwargs):
    if kwargs["created"]:  # only for new users
        new_user = kwargs["instance"]
        # send email to new_user.email ..
        if new_user.email:
            print 'sending email'
            send_templated_mail(
                template_name='join',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[new_user.email, ],
                context={
                    'first_name': new_user.first_name,
                    'signup_date': new_user.date_joined,
                    },
                # Optional:
                # cc=['cc@example.com'],
                # bcc=['bcc@example.com'],
                # headers={'My-Custom-Header':'Custom Value'},
                # template_prefix="my_emails/",
                # template_suffix="email",
                )

post_save.connect(email_new_user, sender=User)
