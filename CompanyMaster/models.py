from django.db import models
from django.contrib.auth.models import User


CENTERFLAG = (
    ('P', 'Profit Center'),
    ('C', 'Cost Center'),
)

class UpdateDate(models.Model):
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    class Meta:
        abstract = True

class UpdateBy(models.Model):
    createdby = models.CharField(verbose_name='Created By', max_length=20)
    updatedby = models.CharField(verbose_name='Updated By', max_length=20)

    class Meta:
        abstract = True


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


class CustomerGroup(UpdateDate):
    customer_group_code = models.CharField(verbose_name="customer group code",
                                           max_length=20, unique=True)
    customer_group_name = models.CharField(verbose_name="customer group name",
                                           max_length=50)
    is_active = models.BooleanField(default=True,
                                    verbose_name="Is Active?")

    def __unicode__(self):
        return self.customer_group_name

    class Meta:
        verbose_name = 'Customer Group'


class OfficeLocation(models.Model):
    name = models.CharField(
        verbose_name="Location Name",
        max_length=30,
        blank=False)
    city = models.CharField("City", max_length=15, blank=False)
    state = models.CharField("State", max_length=20, blank=False)
    zipcode = models.CharField("ZIP or PIN code ", max_length=6, blank=False)
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?"
    )
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.name, self.city)


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


class Department(UpdateDate, UpdateBy):
    code = models.CharField(
        unique=True,
        verbose_name="Department Code",
        max_length=10,
    )
    name = models.CharField(
        verbose_name="Department Name",
        max_length=40,
        blank=False)
    head = models.ForeignKey(
        User,
        verbose_name="Department Head"
    )
    billable = models.BooleanField(
        verbose_name="Is Billable",
    )
    practices = models.BooleanField(
        verbose_name="Has Practices",
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

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
        return u'{0} - {1}'.format(self.department.name, self.name)


class Holiday(models.Model):
    name = models.CharField(verbose_name="Holiday Name",
                            max_length=100,
                            null=True,
                            blank=True)
    date = models.DateField(verbose_name="Holiday Date")
    location = models.ManyToManyField(OfficeLocation, default=None)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    remark = models.CharField(verbose_name="remark",
                              max_length=100,
                              default=None,
                              null=True,
                              blank=True
                              )

    def __unicode__(self):
        return unicode(self.name)


class HRActivity(models.Model):
    name = models.CharField(verbose_name="Event Name",
                            max_length=100,
                            default=None)
    date = models.DateField(verbose_name="Event Date")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name = 'HR Activity'
        verbose_name_plural = 'HR Activities'


class BusinessUnit(models.Model):
    name = models.CharField(
        verbose_name="Business Unit Name",
        max_length=40,
        blank=False)
    new_bu_head = models.ManyToManyField(User, blank=True,
                                         related_name='New_BU_Head',
                                         verbose_name="Business Unit Head")
    centerType = models.CharField(max_length=2,
                                  choices=CENTERFLAG,
                                  verbose_name='Type of center',
                                  default=None)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class DataPoint(models.Model):
    bu = models.ForeignKey(BusinessUnit,
                           verbose_name='BU',
                           blank=False, null=False)
    name = models.CharField(
        verbose_name="Service Line",
        max_length=40,
        blank=False)
    lead = models.ForeignKey(User, verbose_name='Lead',
                             blank=False, null=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Service Line'
        verbose_name_plural = 'Service Lines'


class Region(UpdateDate, UpdateBy):
    region_code = models.CharField(verbose_name="region code",
                                   max_length=10,
                                   unique=True)
    region_name = models.CharField(verbose_name="region name",
                                   max_length=50)
    is_active = models.BooleanField(default=True,
                                    verbose_name="Is Active?")

    def __unicode__(self):
        return self.region_code

    class Meta:
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'


class Currency(UpdateDate):
    currency_code = models.CharField(verbose_name="currency code",
                                     max_length=10,
                                     unique=True)
    currency_name = models.CharField(verbose_name="currency name",
                                     max_length=50)
    default = models.BooleanField(default=True,
                                  verbose_name="Default"
                                  )
    is_active = models.BooleanField(default=True,
                                    verbose_name="Is Active?")

    def __unicode__(self):
        return self.currency_name

    class Meta:
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'


class Country(UpdateDate):
    country_code = models.CharField(verbose_name="Country Code",
                                    max_length=20,
                                    unique=True)
    country_name = models.CharField(verbose_name="Country Name",
                                    max_length=50)
    region_code = models.ForeignKey(Region,
                                    verbose_name="Region code")
    is_active = models.BooleanField(default=True,
                                    verbose_name="Is Active?")
    privacy_rule = models.CharField(verbose_name="Privacy Rule",
                                    max_length=10,
                                    null=True,
                                    blank=True
                                    )
    currency_code = models.ForeignKey(Currency,
                                      verbose_name="Currency Code")

    def __unicode__(self):
        return self.country_name

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'


class Company(UpdateDate):
    company_name = models.CharField(verbose_name="company name",
                                    max_length=40)
    company_legal_name = models.CharField(verbose_name="company legal name",
                                          max_length=50)
    country = models.ForeignKey(Country,
                                verbose_name="country")
    legal_HQ_address = models.TextField(verbose_name="legal head quarter address",
                                        null=True,
                                        blank=True
                                        )
    legal_HQ_city = models.CharField(verbose_name="legal head quarter city",
                                     max_length=20,
                                     null=True,
                                     blank=True
                                     )
    legal_HQ_state = models.CharField(verbose_name="legal head quarter state",
                                      max_length=20,
                                      null=True,
                                      blank=True
                                      )
    legal_HQ_zipcode = models.CharField(verbose_name="legal head quarter zipcode",
                                        max_length=10,
                                        null=True,
                                        blank=True
                                        )

    def __unicode__(self):
        return self.company_name

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'


class PnL(UpdateDate):
    name = models.CharField(
        verbose_name="PnL Name",
        max_length=20,
        unique=True
    )
    description = models.CharField(
        verbose_name="PnL Description",
        max_length=40,
        blank=True,
        null=True
    )
    owner = models.ForeignKey(User)
    is_active = models.BooleanField(
        default=True,
        verbose_name="Is Active"
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'PNL'
        verbose_name_plural = 'PNLS'


class Practice(UpdateDate, UpdateBy):
    code = models.CharField(
        unique=True,
        verbose_name="Practice Code",
        max_length=10,
    )
    name = models.CharField(
        verbose_name="Practice Name",
        max_length=20,
    )
    department = models.ForeignKey(Department,
                                   blank=True,
                                   null=True
                                   )
    head = models.ForeignKey(User)
    sub_practice = models.BooleanField(
        verbose_name="Has Sub Practice",
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Practice'
        verbose_name_plural = 'Practices'


class SubPractice(UpdateDate, UpdateBy):
    code = models.CharField(
        unique=True,
        verbose_name="Sub Practice Code",
        max_length=40,
    )
    name = models.CharField(
        verbose_name="Sub Practice Name",
        max_length=40,
    )
    practice = models.ForeignKey(Practice)
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Sub Practice'
        verbose_name_plural = 'Sub Practices'

class CareerBand(UpdateDate):
    code = models.CharField(
        unique=True,
        verbose_name="Career Band Code",
        max_length=40,
    )
    description = models.CharField(
        verbose_name="Career Band Name",
        max_length=40,
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

    def __unicode__(self):
        return self.code

    class Meta:
        verbose_name = 'Career Band'
        verbose_name_plural = 'Career Bands'


class Role(UpdateDate):
    code = models.CharField(
        unique=True,
        verbose_name="Role Code",
        max_length=10,
    )
    name = models.CharField(
        verbose_name="Role Name",
        max_length=20,
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'


class Designation(UpdateDate, UpdateBy):
    name = models.CharField(
        verbose_name="Designation Name",
        max_length=40,
        unique=False,
    )
    role = models.ForeignKey(Role)
    career_band_code = models.ForeignKey(
        CareerBand
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
    )
    steps = models.IntegerField(verbose_name="Ladder Step")

    def __unicode__(self):
        return self.name + " | " + self.role.name

    class Meta:
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'


class KRA(UpdateDate, UpdateBy):
    designation = models.ForeignKey(Designation)
    series = models.IntegerField()
    narration = models.TextField(
        verbose_name="KRA Narration",
    )
    is_active = models.BooleanField(
        verbose_name="Is Active",
        default=True,
    )

    def __unicode__(self):
        return self.narration

    class Meta:
        verbose_name = 'KRA'
        verbose_name_plural = 'KRAs'


class Customer(models.Model):
    name = models.CharField(verbose_name='Customer Name',
                            max_length=100,
                            null=False,
                            blank=False,
                            unique=True)
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
    Crelation = models.ForeignKey(User, default=None, related_name="Relation",
                                  verbose_name='Account relationship manager',
                                  blank=True, null=True)
    Cdelivery = models.ForeignKey(User, default=None,
                                  verbose_name='Account delivery manager',
                                  blank=True, null=True)
    cContact = models.CharField(
        verbose_name="Customer contact",
        null=False,
        blank=False,
        max_length=100,
        default=None
    )
    CType = models.ForeignKey(CustomerType, default=None,
                              verbose_name='Business Segment',
                              blank=False, null=False)
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?"
    )
    address = models.CharField(
        verbose_name="Address",
        default=None,
        max_length=100,
        blank=False)
    customergroup = models.ForeignKey(CustomerGroup,
                                      verbose_name="Customer Group",
                                      null=True,
                                      blank=True)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    pnl = models.ForeignKey(PnL, default=None, null=True, blank=True)
    country_code = models.ForeignKey(Country, default=None, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)









