from CustomApp.models import AbstractProcess, AbstractEntity,content_file_name
from django.contrib.auth.models import User
from django.db.models import (
    Model,
    CharField,
    ForeignKey,
    IntegerField,
    TextField,
    FileField,
    DateField,
)
from CustomApp.constants import PROCESS_STATUS


class Reimburse(AbstractProcess):
    bill_no = CharField(max_length=50)
    bill_date = DateField()
    vendor_name = CharField(max_length=50)
    nature_of_expenses = TextField(null=True, blank=True)
    amount = IntegerField()
    attachment = FileField(upload_to=content_file_name, blank=True, null=True, verbose_name='Attachment')


class Transaction(AbstractEntity):
    reimburse = ForeignKey(Reimburse)
    approved_by = ForeignKey(User)
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)
