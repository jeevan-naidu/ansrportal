from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


class SalesforceData(models.Model):

    """ This model will contain all the data from the salesforce.
    The exported files from salesforce will be uploaded to this model on regualar basis.
    The opportunity number will be unique"""

    opportunity_number = models.IntegerField(help_text="8 digit number starting with 201",
                                           verbose_name="SF\Opportunity Number",
                                           validators=[MinValueValidator(20100000),
                                                       MaxValueValidator(99999999)],
                                            unique=True)
    opportunity_name = models.CharField(max_length=300)
    business_unit = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=100,
                                    verbose_name="Customer Contact")
    account_name = models.CharField(max_length=100, blank=True, null=True)
    value = models.DecimalField(verbose_name="Project Value(in $)", max_digits=20, decimal_places=5)
    probability = models.IntegerField()
    start_date = models.DateField(verbose_name="Estimated End Date", blank=True, null=True)
    end_date = models.DateField(verbose_name="Estimated Start Date", blank=True, null=True)
    status = models.CharField(max_length=100, blank=True, null=True)

    def __unicode__(self):
        """ return unicode strings """

        return '%s' % self.opportunity_number

    class Meta:
        verbose_name_plural = "Salesforce Data"




