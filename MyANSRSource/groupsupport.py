import django_auth_ldap.backend
from django.contrib.auth.models import Group
from django.conf import settings



def update_user_flags(sender, user=None, ldap_user=None, **kwargs):
    # Remember that every attribute maps to a list of values
    if user:
        usergrp = Group.objects.get_by_natural_key(name=settings.MYANSRSOURCE_GROUP)
        user.is_active = True
        # user.is_staff = True
        user.groups.add(usergrp)


django_auth_ldap.backend.populate_user.connect(update_user_flags)
