from django.db import models

# Create your models here.
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
        return self.name + '::' + self.city


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
        return self.department.name + '::' + self.name


class BusinessUnit(models.Model):
    name = models.CharField(
        verbose_name="Business Unit Name",
        max_length=40,
        blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name
