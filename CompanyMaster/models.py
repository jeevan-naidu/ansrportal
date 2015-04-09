from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class CustomerType(models.Model):
    name = models.CharField(
        verbose_name="Type of Customer",
        max_length=30,
        blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(verbose_name='Customer Name',
                            max_length=100,
                            null=False,
                            blank=False)
    internal = models.BooleanField(
        blank=False,
        default=False,
        null=False,
        verbose_name="Internal Customer"
    )
    customerCode = models.CharField(
        verbose_name="Customer Code",
        null=False,
        blank=False,
        max_length=3,
        default=None
    )
    location = models.CharField(
        verbose_name="Location",
        null=False,
        blank=False,
        max_length=100,
        default=None
    )
    seqNumber = models.PositiveIntegerField(null=False, default=1,
                                            verbose_name='Project ID Sequence')
    relatedMember = models.ManyToManyField(
        User,
        verbose_name="Select Account Relationship team",
        blank=False,
        null=False
    )
    CType = models.ForeignKey(CustomerType, default=None,
                              verbose_name='Customer Type',
                              blank=False, null=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class OfficeLocation(models.Model):
    name = models.CharField(
        verbose_name="Location Name",
        max_length=30,
        blank=False)
    city = models.CharField("City", max_length=15, blank=False)
    state = models.CharField("State", max_length=20, blank=False)
    zipcode = models.CharField("ZIP or PIN code ", max_length=6, blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name + ' - ' + self.city


class Training(models.Model):
    location = models.ForeignKey(OfficeLocation,
                                 verbose_name='Location',
                                 blank=False, null=False)
    batch = models.CharField(
        verbose_name="Batch",
        null=False,
        blank=False,
        max_length=30,
        default=None
    )
    exercise = models.CharField(
        verbose_name="Exercise",
        null=False,
        blank=False,
        max_length=30,
        default=None
    )
    trainer = models.ForeignKey(
        User,
        verbose_name="Trainer",
        blank=False,
        null=False
    )
    trainingDate = models.DateField(default=None, verbose_name="Start Date")
    endDate = models.DateField(default=None, verbose_name="End Date")
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.exercise + ' - ' + self.batch


class Department(models.Model):
    name = models.CharField(
        verbose_name="Department Name",
        max_length=40,
        blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class Division(models.Model):
    department = models.ForeignKey(Department)
    name = models.CharField(
        verbose_name="Sub Department Name",
        max_length=40,
        blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.department.name + ' - ' + self.name


class Holiday(models.Model):
    name = models.CharField(verbose_name="Holiday Name",
                            max_length="100",
                            null=True,
                            blank=True)
    date = models.DateField(verbose_name="Holiday Date")
    location = models.ManyToManyField(OfficeLocation, default=None)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class BusinessUnit(models.Model):
    name = models.CharField(
        verbose_name="Business Unit Name",
        max_length=40,
        blank=False)
    bu_head = models.OneToOneField(User, default=None,
                                   verbose_name="Business Unit Head")
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name
