from CustomApp.models import AbstractProcess, AbstractEntity,content_file_name
from django.contrib.auth.models import User
from django.db import models
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    IntegerField,
    TextField,
    FileField,
    DateField,
    BooleanField,
)
from CustomApp.constants import PROCESS_STATUS

class Laptops(models.Model):
    laptop_id = CharField(max_length=50)
    brand = CharField(max_length=20)
    avaliable = BooleanField(default=True)

    def __unicode__(self):
        avalibility = (lambda avaliable : "Avaliable" if avaliable else "UnAvaliable")(self.avaliable)
        return self.laptop_id + " | " + avalibility

class Laptop(AbstractProcess):

    laptop = ForeignKey(Laptops)
    from_date = DateField()
    to_date = DateField()
    reason = TextField(null=True, blank=True)
    # attachment = FileField(upload_to=content_file_name, blank=True, null=True, verbose_name='Attachment')

class Transaction(AbstractEntity):

    laptop = ForeignKey(Laptop)
    approved_by = ForeignKey(User, related_name='%(class)s_approved_user')
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)

