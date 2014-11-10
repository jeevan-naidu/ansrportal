from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # This field is required.
    # user = models.OneToOneField(User,related_name="user")
    # Other fields here
    uid = models.CharField(max_length=254)
    cn = models.CharField(max_length=254)
    sn = models.CharField(max_length=254)
    givenName = models.CharField(max_length=254)
    userPassword = models.CharField(max_length=254)
    loginShell = models.CharField(max_length=254)
    uidNumber = models.IntegerField(null=True)
    gidNumber = models.IntegerField(null=True)
    homeDirectory = models.CharField(max_length=254)
    gecos = models.CharField(max_length=254)
    mail = models.EmailField(max_length=254)

#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        UserProfile.objects.create(user=instance)
    #UserProfile.objects.get_or_create(user=instance)

#post_save.connect(create_user_profile, sender=User)

