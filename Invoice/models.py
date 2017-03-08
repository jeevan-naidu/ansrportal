from CustomApp.models import AbstractProcess, AbstractEntity
from django.contrib.auth.models import User
from Leave.models import content_file_name
from django.db.models import (
    CharField,
    ForeignKey,
    IntegerField,
    TextField,
    ManyToManyField,
    FileField
)
from CustomApp.constants import PROCESS_STATUS


class Invoice(AbstractProcess):
    title = CharField(max_length=50)
    reason = TextField(null=True, blank=True, max_length=2000)
    ppl_involved = ManyToManyField(User)
    atachement = FileField(upload_to=content_file_name, blank=True, null=True, verbose_name='Attachment')
    amount = IntegerField()


class InvoiceTransaction(AbstractEntity):
    invoice = ForeignKey(Invoice)
    approved_by = ForeignKey(User)
    status = CharField(choices=PROCESS_STATUS, max_length=20)
    reason = TextField(null=True, blank=True)
