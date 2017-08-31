from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
# Create your models here.


class SalesforceData(models.Model):

    """ This model will contain all the data from the salesforce.
    The exported files from salesforce will be uploaded to this model on regualar basis.
    The opportunity number will be unique"""
    user = models.ForeignKey(User, default=35)
    opportunity_number = models.IntegerField(help_text="8 digit number starting with 201",
                                           verbose_name="SF\Opportunity Number",
                                           validators=[MinValueValidator(20100000),
                                                       MaxValueValidator(99999999)],
                                            unique=True)
    opportunity_name = models.CharField(max_length=300)
    business_unit = models.CharField(max_length=100, blank=True, null=True)
    customer_contact = models.CharField(max_length=100,
                                    verbose_name="Customer Contact", blank=True, null=True)
    account_name = models.CharField(max_length=100)
    value = models.DecimalField(verbose_name="Project Value(in $)", max_digits=20, decimal_places=5,
                                blank=True, null=True)
    probability = models.IntegerField(blank=True, null=True)
    estimate_start_date = models.DateField(verbose_name='Estimated Start Date', blank=True, null=True)
    estimate_end_date = models.DateField(verbose_name="Estimated End Date", blank=True, null=True)
    planned_start_date = models.DateField(verbose_name='Planned Start Date', blank=True, null=True)
    planned_end_date = models.DateField(verbose_name="Planned End Date", blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)
    updated_date = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        """ return unicode strings """

        return '%s' % self.opportunity_number

    class Meta:
        verbose_name_plural = "Salesforce Data"