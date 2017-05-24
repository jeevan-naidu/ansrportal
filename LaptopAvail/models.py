from CustomApp.models import AbstractProcess, AbstractEntity
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
RETURN_STATUS = (("initiated", "INITIATED"), ('returned', 'RETURNED'), ('approved', 'APPROVED'))


class Laptops(models.Model):
    laptop_id = CharField(max_length=50)
    brand = CharField(max_length=20)
    service_tag = CharField(max_length=50)
    avaliable = BooleanField(default=True)
    location = CharField(max_length=50)

    def __unicode__(self):
        avalibility = (lambda avaliable : "Avaliable" if avaliable else "UnAvaliable")(self.avaliable)
        return self.laptop_id + " | " + avalibility


class LaptopApply(AbstractProcess):
    laptop = ForeignKey(Laptops)
    from_date = DateField()
    to_date = DateField()
    reason = TextField(null=True, blank=True)
    return_status = CharField(max_length=20, choices=RETURN_STATUS, default=None)


class Transaction(AbstractEntity):
    laptop = ForeignKey(LaptopApply)
    approved_by = ForeignKey(User, related_name='%(class)s_approved_user')
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)

