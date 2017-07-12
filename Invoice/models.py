from CustomApp.models import AbstractProcess, AbstractEntity,content_file_name
from django.contrib.auth.models import User
from MyANSRSource.models import Project
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    IntegerField,
    TextField,
    FileField,
    DateField,
)
from CustomApp.constants import PROCESS_STATUS, PAYMENT_STATUS


class Invoice(AbstractProcess):
    project = ForeignKey(Project)
    milestone_date = DateField()
    milestone_name = CharField(max_length=50)
    description = TextField(null=True, blank=True)
    closed_on_date = DateField()
    amount = IntegerField()


class Transaction(AbstractEntity):
    invoice = ForeignKey(Invoice)
    approved_by = ForeignKey(User, related_name='%(class)s_approved_by')
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)


class Payment(AbstractEntity):
    invoice = ForeignKey(Invoice)
    approved_by = ForeignKey(User, related_name='%(class)s_approved_by')
    payment_status = CharField(choices=PAYMENT_STATUS, max_length=10)
    payment_reason = TextField(null=True, blank=True)