import logging
logger = logging.getLogger('MyANSRSource')
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from CompanyMaster.models import PnL, Practice, SubPractice, Department, Designation, Company, UpdateDate, UpdateBy
import CompanyMaster
fs = FileSystemStorage(location='employee/emp_photo')

GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
    )

MARITAL_CHOICES = (
    ('MA', 'Married'),
    ('WD', 'Windowed'),
    ('SE', 'Seperated'),
    ('DV', 'Divorced'),
    ('SG', 'Single'),
    )

BLOOD_GROUP_CHOICES = (
    ('00', 'A+'),
    ('01', 'A-'),
    ('02', 'B+'),
    ('03', 'B-'),
    ('04', 'O+'),
    ('05', 'O-'),
    ('06', 'AB+'),
    ('07', 'AB-'),
    )

COLOR_CHOICES = (
    ('violet', 'Violet'),
    ('indigo', 'Indigo'),
    ('blue', 'Blue'),
    ('green', 'Green'),
    ('yellow', 'Yellow'),
    ('orange', 'Orange'),
    ('red', 'Red')
)

CATEGORY_CHOICES = (
    ('FT', 'Fulltime Employee'),
    ('PT', 'Parttime Employee'),
    ('IN', 'Intern'),
    ('CT', 'Contractor'),
    )


OVERTIMEPLAN_CHOICES = (('CB', 'Compensatory Leave'),
                        ('LP', 'Leave Pay'))


RELATION_CHOICES = (
    ('FA', 'Father'),
    ('MO', 'Mother'),
    ('SP', 'Spouse'),
    ('C1', 'Child1'),
    ('C2', 'Child2'),
    ('OO', 'Others'),
    )

EMP_STATUS_CHOICES = (
    ('00', 'InActive'),
    ('01', 'Active'),
    )

ADDRESSTYPE_CHOICES = (
    ('PR', 'Permanent'),
    ('TM', 'Temporary'),
    )


NATURE_OF_EDUCATION = (
    ('FT', 'Full-time'),
    ('PT', 'Part-time'),
)


# used for employee without auto_now_add for date time field
class TimeStampAbstractModel(models.Model):
    created_on = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by')
    updated_on = models.DateTimeField(blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by', blank=True, null=True)

    class Meta:
        abstract = True


class Designation(models.Model):
    name = models.CharField(
        verbose_name="Title",
        max_length=40,
        blank=False)
    billable = models.BooleanField(default=True, verbose_name='Billable')
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
        return self.name


class EmpAddress(models.Model):

    class Meta:
        verbose_name_plural = 'Addresses'

    employee = models.ForeignKey(User)
    address_type = models.CharField('Address Type',
                                    max_length=2,
                                    choices=ADDRESSTYPE_CHOICES,
                                    default='TM')
    address1 = models.CharField(
        verbose_name="Address 1",
        max_length=100,
        blank=False)
    address2 = models.CharField(
        verbose_name="Address 2",
        max_length=100,
        blank=False)
    city = models.CharField("City", max_length=30, blank=False)
    state = models.CharField("State", max_length=30, blank=False)
    zipcode = models.CharField("Zip Code", max_length=10, blank=False)

    def __unicode__(self):
        return u'{0}, {1}, {2}, {3}, {4}'.format(
            self.address1,
            self.address2,
            self.city,
            self.state,
            self.zipcode)

""" This class is an extension of the Django user class.  The fields in the
User model can be found here.
https://docs.djangoproject.com/en/dev/ref/contrib/auth/ """


class Employee(TimeStampAbstractModel):
    # User model will have the usual fields.  We will have the remaining ones
    # here
    user = models.OneToOneField(User, verbose_name="User")
    manager = models.ForeignKey('self', verbose_name="Manager",
                                blank=True, null=True,
                                related_name="Manager", default=None)
    status = models.BooleanField(default=True)
    practice = models.ForeignKey(Practice, default=None, verbose_name="Practice", blank=True, null=True)
    '''
    ================================================
    Basic Employee Attributes
    ================================================
    '''
    # No middlename in user model !
    middle_name = models.CharField("Middle Name", max_length=15, blank=True)
    # Gender
    gender = models.CharField(
        "Gender",
        max_length=2,
        choices=GENDER_CHOICES,
        blank=False)
    date_of_birthO = models.DateField("Official DOB", blank=False, default=None)
    date_of_birthR = models.DateField(
        "Alternate DOB",
        blank=True,
        null=True,
        )
    # Can we make this a choice field?
    nationality = models.CharField("Nationality", max_length=30, blank=False)
    marital_status = models.CharField(
        "Marital Status",
        max_length=10,
        choices=MARITAL_CHOICES,
        blank=True,
        null=True
    )
    wedding_date = models.DateField(verbose_name='Wedding Date',
                                    null=True,
                                    blank=True)
    blood_group = models.CharField(
        "Blood Group",
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True)
    mobile_phone = models.CharField(
        "Mobile Phone",
        max_length=15,
        unique=True,
        blank=True)
    land_phone = models.CharField(
        "Landline Number",
        max_length=15, blank=True)
    emergency_phone = models.CharField(
        "Emergency Contact Number",
        max_length=15,
        unique=True,
        null=True,
        blank=True)
    personal_email = models.EmailField(
        "Personal E-mail",
        max_length=250,
        null=True,
        blank=True,
        unique=True)
    passport_number = models.CharField(
        "Passport Number",
        max_length=10,
        unique=True,
        null=True,
        blank=True)

    photo = models.ImageField(storage=fs,
                              verbose_name="Employee Photo")

    '''
    =========================================================
    Company assigned attributes for the employee on joining
    =========================================================
    '''
    # Business unit to which this employee belongs
    business_unit = models.ForeignKey('CompanyMaster.BusinessUnit')
    # user's default office location
    location = models.ForeignKey('CompanyMaster.OfficeLocation')
    # Corporates have already assigned employee Ids.
    employee_assigned_id = models.CharField(
        "Employee ID",
        max_length=15,
        primary_key=True,
        blank=False)
    idcard = models.CharField(
        "Access Card Number",
        max_length=15,
        unique=True,
        blank=False)
    # division = models.ForeignKey('CompanyMaster.Division')
    category = models.CharField(
        "Employment Category",
        max_length=3,
        choices=CATEGORY_CHOICES,
        blank=False)
    designation = models.ForeignKey(Designation)
    exprience = models.IntegerField(
        "Experience in Months",
        blank=True,
        null=True
    )
    color = models.CharField(
        "Color",
        max_length=10,
        choices=COLOR_CHOICES,
        blank=True,
        null=True,
    )

    '''
    ============================
    Key dates for the employee
    ============================
    '''
    joined = models.DateField("Joining Date", blank=False)
    confirmation = models.DateField("Confirmation Date", blank=False)
    last_promotion = models.DateField("Probation End Date", blank=False)
    resignation = models.DateField("Resignation Date", null=True, blank=True)
    exit = models.DateField("Exit Date", null=True, blank=True)

    '''
    =================================================
    Financial details for Salary, Insurance etc.,
    =================================================
    '''
    PAN = models.CharField(
        "PAN Number",
        max_length=10,
        null=True,
        blank=True,
        unique=True)
    PF_number = models.CharField(
        "Provident Fund Number",
        max_length=14,
        blank=True)
    uan = models.IntegerField(
        "Universal account number",
        blank=True,
        null=True,
        unique=True)
    bank_name = models.CharField(verbose_name="Bank Name",
                                 max_length=70, blank=True, null=True)
    bank_branch = models.CharField(verbose_name="Branch Name",
                                   max_length=70, blank=True, null=True)
    bank_account = models.IntegerField(
        "Account Number",
        blank=True,
        null=True,
        unique=True)
    bank_ifsc_code = models.CharField(
        "IFSC Code",
        max_length=20, blank=True, null=True)
    group_insurance_number = models.CharField(
        "Group Insurance Number",
        max_length=30,
        blank=True)
    esi_number = models.CharField(
        "ESI Number",
        max_length=30,
        null=True,
        blank=True)
    '''
    ================================================
    For 360 degree feedback system
    ================================================
    '''

    def __unicode__(self):
        return u'{0}|{1},{2}'.format(
            self.employee_assigned_id,
            self.user.first_name,
            self.user.last_name)

    def get_full_name(self):
        return self.first_name+''+self.last_name


class EmployeeArchive(TimeStampAbstractModel):
    user = models.ForeignKey(User, verbose_name="User")
    employee_assigned_id = models.CharField(
        "Employee ID",
        max_length=15,
        blank=True)

    manager = models.ForeignKey(Employee, verbose_name="Manager",
                                blank=True, null=True,
                                related_name="Manager", default=None)
    designation = models.ForeignKey(Designation)
    archive_date = models.DateField("Archive Date", auto_now_add=True)
    business_unit = models.ForeignKey('CompanyMaster.BusinessUnit')
    location = models.ForeignKey('CompanyMaster.OfficeLocation')
    practice = models.ForeignKey(Practice, default=None, verbose_name="Practice", blank=True, null=True)

    def __unicode__(self):
        return unicode(self.user)


def DefaultPermission(sender, instance, **kwargs):
    try:
        g = Group.objects.get(name='myansrsourceUsers')
        g.user_set.add(instance)
    except ObjectDoesNotExist:
        logger.error(
            'Unable to assign group to user, group is not having a match')

post_save.connect(DefaultPermission,
                  sender=User,
                  dispatch_uid="Add Default Permission")


class TeamMember(User):

    class Meta:
        proxy = True
        app_label = 'auth'
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

post_save.connect(DefaultPermission,
                  sender=TeamMember,
                  dispatch_uid="Add Default Permission")


class FamilyMember(models.Model):
    employee = models.ForeignKey(User)
    name = models.CharField("Name", max_length=50, blank=False)
    gender = models.CharField(
        verbose_name='Gender',
        max_length=1,
        choices=GENDER_CHOICES,
        blank=False,
        default=GENDER_CHOICES[0][0])
    dob = models.DateField("DOB", blank=True, null=True)
    rela_type = models.CharField(
        "Relation Type",
        max_length=50,
        choices=RELATION_CHOICES,
        blank=False)

    def __unicode__(self):
        return u'{0} - {1}'.format(self.name, self.dob)


class Education(models.Model):

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"

    employee = models.ForeignKey(User)
    name = models.CharField("Qualification", max_length=50, blank=False)
    specialization = models.CharField(
        verbose_name='Specialization',
        max_length=30,
        blank=True,
        null=True)
    nature_of_education = models.CharField('Nature of Education',
                                           max_length=2,
                                           blank=False,
                                           choices=NATURE_OF_EDUCATION,
                                           default=NATURE_OF_EDUCATION[0][0])
    from_date = models.DateField("From Date", blank=False)
    to_date = models.DateField("To Date", blank=False)
    institute = models.CharField("Institution", max_length=50, blank=False)
    overall_marks = models.IntegerField(
        "Total Score/GPA",
        blank=False)

    def __unicode__(self):
        return u'{0}({4})-{3} / {1} to {2}'.format(
            self.name,
            self.from_date,
            self.to_date,
            self.institute,
            self.specialization
        )


class PreviousEmployment(models.Model):

    class Meta:
        verbose_name = "Previous Employment"
        verbose_name_plural = "Previous Employment"

    employee = models.ForeignKey(User)
    company_name = models.CharField("Company Name", max_length=150)
    company_address = models.CharField(
        "Company Address",
        max_length=500)
    employed_from = models.DateField(verbose_name="Start Date", null=False)
    employed_upto = models.DateField(verbose_name="End Date", null=False)
    pf_number = models.CharField(
        "PF Number",
        max_length=15,
        null=True,
        blank=True)
    last_ctc = models.DecimalField(
        "Last CTC",
        max_digits=15,
        decimal_places=2)
    reason_for_exit = models.CharField(
        verbose_name="Reason for Exit",
        max_length=50)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.company_name + ':' + \
            str(self.employed_from) + ' ~ ' + str(self.employed_upto)


class Remainder(models.Model):
    user = models.ForeignKey(Employee, default=None)
    name = models.CharField(verbose_name="Event Name",
                            max_length=100
                            )
    startDate = models.DateField(verbose_name="Start Date",
                                 default=timezone.now)
    endDate = models.DateField(verbose_name="End Date",
                               default=timezone.now)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, null=True)
    attdate = models.DateField(null=True, blank=True, verbose_name='Swipe Date')
    swipe_in = models.DateTimeField(null=True, blank=True)
    swipe_out = models.DateTimeField(null=True, blank=True)
    incoming_employee_id = models.CharField(
        max_length=100,
        null=True,
        blank=True)

    class Meta:
        unique_together = ('employee', 'attdate',)
        verbose_name_plural = 'Attendance'
        verbose_name = 'Attendance'


class EmployeeCompanyInformation(UpdateDate, UpdateBy):
    employee = models.ForeignKey(Employee, verbose_name="Employee")
    is_billable = models.BooleanField(default=True, verbose_name="Is Billable")
    billable_date = models.DateField(verbose_name="Effective Date of Billability",
                                     blank=True,
                                     null=True,
                                     default="2017-01-01")
    department = models.ForeignKey(Department, verbose_name="Department")
    designation = models.ForeignKey(CompanyMaster.models.Designation, verbose_name="Designation")
    company = models.ForeignKey(Company, default=None, verbose_name="Company", blank=True, null=True)
    pnl = models.ForeignKey(PnL, default=None, verbose_name="PnL", blank=True, null=True)
    practice = models.ForeignKey(Practice, default=None, verbose_name="Practice", blank=True, null=True)
    sub_practice = models.ForeignKey(SubPractice, default=None, verbose_name="Sub Practice", blank=True, null=True)

    class Meta:
        verbose_name = 'Employee Company Information'
        verbose_name_plural = 'Employees Company Information'

