from CustomApp.models import AbstractProcess, AbstractEntity
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    IntegerField,
    TextField
)
from CustomApp.constants import PROCESS_STATUS


class Reimburse(AbstractProcess):
    title = CharField(max_length=50)
    reason = TextField(null=True, blank=True)
    amount = IntegerField()


class Transaction(AbstractEntity):
    reimburse = ForeignKey(Reimburse)
    approved_by = ForeignKey(User)
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)
