from django.db import models
from django.contrib.auth.models import User
from employee.models import Employee

CENTERFLAG = (
    ('P', 'Profit Center'),
    ('C', 'Cost Center'),
)


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

#
# class Customer(models.Model):
#     name = models.CharField(verbose_name='Customer Name', max_length=100, null=False, blank=False)
#     internal = models.BooleanField(blank=False, default=False, null=False, verbose_name="Internal Customer")
#     customerCode = models.CharField(verbose_name="Customer Code", null=False, blank=False, max_length=3, default=None)
#     location = models.CharField(verbose_name="Location", null=False, blank=False, max_length=100, default=None)
#     seqNumber = models.PositiveIntegerField(null=False, default=1, verbose_name='Project ID Sequence')
#     Crelation = models.ForeignKey(User, default=None, related_name="Relation", verbose_name='Account relationship manager', blank=True, null=True)
#     Cdelivery = models.ForeignKey(User, default=None, verbose_name='Account delivery manager', blank=True, null=True)
#     cContact = models.CharField(verbose_name="Customer contact", null=False, blank=False, max_length=100, default=None)
#     CType = models.ForeignKey(CustomerType, default=None, verbose_name='Customer Type', blank=False, null=False)
#     active = models.BooleanField( blank=False, default=True, null=False, verbose_name="Is Active?")
#     address = models.CharField(verbose_name="Address", default=None, max_length=100, blank=False)
#     createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
#     updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
#
#     def __unicode__(self):
#         return unicode(self.name)


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


class Department(models.Model):
    name = models.CharField(
        verbose_name="Department Name",
        max_length=40,
        blank=False)
    department_head = models.ForeignKey(Employee, verbose_name='Head')
    department_centre_type = models.CharField(max_length=200, choices=CENTERFLAG)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

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


class HRActivity(models.Model):
    name = models.CharField(verbose_name="Event Name",
                            max_length="100",
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
    new_bu_head = models.ManyToManyField(User, null=True, blank=True,
                                         related_name='New BU Head',
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










class Region(models.Model):
    region_name = models.CharField(max_length=200, verbose_name = 'Region Name')
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.region_name

class Currency(models.Model):
    currency_code = models.CharField(max_length = 200, verbose_name = 'Currency Code')
    currency_name = models.CharField(max_length = 200, verbose_name = 'Currency Name')
    default = models.CharField(max_length = 200, verbose_name = 'Default', blank=False, null=False)
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.currency_name

class Country(models.Model):
    region_name = models.ForeignKey(Region, verbose_name = 'Region Name')
    country_name = models.CharField(max_length = 200, verbose_name = 'Country')
    country_code = models.CharField(max_length = 200,verbose_name = 'Country Code', blank=False, null=False)
    currency = models.ForeignKey(Currency, verbose_name = 'Currency Code')
    privacy_rule = models.CharField(max_length = 200, verbose_name = 'Privacy Rule',  blank=False, null=False)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.country_name

# class Location(models.Model):
#     location_name = models.CharField(max_length = 200, verbose_name = 'Location Name')
#     country = models.ForeignKey(Country, verbose_name = 'Country')
#     street1 = models.CharField(max_length = 200, verbose_name = 'Street1')
#     street2 = models.CharField(max_length = 200, verbose_name = 'Street2', blank=False, null=False)
#     street3 = models.CharField(max_length = 200, verbose_name = 'Street3', blank=False, null=False)
#     city = models.CharField(max_length = 200, verbose_name = 'City')
#     postal_code = models.CharField("ZIP or PIN code", max_length=6, blank=False, null=False)
#     active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")
#
#     def __unicode__(self):
#         return self.location_name


class Company(models.Model):
    company_name = models.CharField(max_length = 200, verbose_name = 'Company Name')
    company_legal_name = models.CharField(max_length = 200, verbose_name = 'Company Legal Name')
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.company_name


class Location(models.Model):
    location_name = models.CharField(max_length=200, verbose_name='Location Name')
    country = models.ForeignKey(Country, verbose_name = 'Country')
    company = models.ForeignKey(Company)
    street1 = models.CharField(max_length = 200, verbose_name = 'Street1')
    street2 = models.CharField(max_length = 200, verbose_name = 'Street2', blank=True, null=True)
    street3 = models.CharField(max_length = 200, verbose_name = 'Street3', blank=True, null=True)
    city = models.CharField(max_length = 200, verbose_name = 'City')
    postal_code = models.CharField("ZIP or PIN code", max_length=10)
    HQ = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is HQ?")
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.location_name


class SupportTask(models.Model):
    task_name = models.CharField(max_length=100)
    #task_description = models.CharField(max_length = 100, blank = True, null=True)
    department = models.ForeignKey(Department)
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.task_name


class Practice(models.Model):
    practice_name  = models.CharField(max_length = 200, verbose_name = 'Practice name')
    department = models.ForeignKey(Department, verbose_name = 'Department')
    practice_head = models.ForeignKey(Employee, verbose_name='Practice Head')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.practice_name


class SubPractice(models.Model):
    sub_practice_name = models.CharField(max_length = 200, verbose_name = 'Sub Practice name')
    pratice = models.ForeignKey(Practice, verbose_name = 'Practice Name')
    sub_practice_lead = models.ForeignKey(Employee, verbose_name='Sub Practice Head')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.sub_practice_name

    class Meta:
        verbose_name = 'Sub Practice'

class Role(models.Model):
    role_name = models.CharField(max_length = 200, verbose_name = 'Role')
    role_definition = models.CharField(max_length = 1000, verbose_name = 'Role Definition')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.role_name


class CareerBand(models.Model):
    career_band_name = models.CharField(max_length = 200, verbose_name = 'Career Band')
    description = models.CharField(max_length = 200, verbose_name = 'Description')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.career_band_name

    class Meta:
        verbose_name = 'Career Band'


class Designation(models.Model):
    designation_name = models.CharField(max_length = 200, verbose_name = 'Designation Name')
    career_band_name = models.ForeignKey(CareerBand, verbose_name = 'Career Band Name')
    role = models.ManyToManyField(Role, verbose_name = 'Role')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.designation_name


class KRA(models.Model):
    designation_name = models.ForeignKey(Designation, verbose_name = 'Designation')
    KRA_narration = models.CharField(max_length = 1000, verbose_name = 'KRA Narration')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.designation_name

class CareerLadderHeader(models.Model):
    career_ladder_header = models.CharField(max_length = 200, verbose_name = 'Career Ladder Header')
    description = models.CharField(max_length = 500, verbose_name = 'Description')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.career_ladder_name

    class Meta:
        verbose_name = 'Career Ladder Header'

class CareerLadder(models.Model):
    career_ladder_header = models.ForeignKey(CareerLadderHeader, verbose_name = 'Career Ladder Header')
    ladder_step = models.PositiveIntegerField(verbose_name = 'Ladder Step(Positive Integer)')
    designation = models.ForeignKey(Designation, verbose_name = 'Designation')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.career_ladder_header

    class Meta:
        verbose_name = 'Career Ladder Header'


class PnL(models.Model):
    pnl_name = models.CharField(max_length = 200, verbose_name = 'PNL Name')
    pnl_description = models.CharField(max_length = 500, verbose_name = 'PNL Description')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.pnl_name


class BusinessSegment(models.Model):
    segment_name = models.CharField(max_length = 200, verbose_name = 'Segment Name')
    pnl = models.ForeignKey(PnL, verbose_name = 'PNL Name')
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.segment_name


class GroupCustomer(models.Model):

    customer_group_name = models.CharField(max_length=200)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.customer_group_name


class Customer(models.Model):
    """Customer link with salesforce """

    customer_code = models.CharField(max_length=200, verbose_name='Customer Code')
    customer_name = models.CharField(max_length=200, verbose_name='Customer Name')
    project_id_sequence = models.PositiveIntegerField(null=False, verbose_name='Project ID Sequence')
    group_customer_name = models.ForeignKey(GroupCustomer, blank=True, null=True)
    customer_contact = models.CharField(max_length=200, verbose_name='Customer Contact', blank=True, null=True)
    business_segment = models.ForeignKey(BusinessSegment)
    customer_type = models.ForeignKey(CustomerType)
    account_relationship_manager = models.ForeignKey(Employee, related_name='Account Relationship Manager', blank=True, null=True)
    account_delivery_manager = models.ForeignKey(Employee, related_name='Account Delivery Manager', blank=True, null=True)
    HQ_address = models.ForeignKey(Location, related_name='HQ Address')
    bill_to_address = models.ForeignKey(Location, related_name='Bill To Address', blank=True, null=True)
    bill_to_email = models.EmailField(max_length=200, verbose_name='Bill To Email', blank=True, null=True)
    ship_to_address = models.ForeignKey(Location, related_name='Ship To Address', blank=True, null=True)
    ship_to_email = models.EmailField(max_length=200, verbose_name='Ship To Email', blank=True, null=True)
    internal = models.BooleanField(blank=False, default=False, null=False, verbose_name="Internal Customer")
    account_receivable_email = models.EmailField(max_length=200, verbose_name='Account Receivable Email', blank=True, null=True)
    createdon = models.DateTimeField(verbose_name="created Date", auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date", auto_now=True)
    active = models.BooleanField(blank=False, default=True, null=False, verbose_name="Is Active?")

    def __unicode__(self):
        return self.customer_name
