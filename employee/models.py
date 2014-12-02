from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

fs = FileSystemStorage(location='employee/emp_photo')

GENDER_CHOICES = (
    ('00', 'Male'),
    ('01', 'Female'),
    )

MARITAL_CHOICES = (
    ('00', 'Married'),
    ('01', 'Windowed'),
    ('02', 'Seperated'),
    ('03', 'Divorced'),
    ('04', 'Single'),
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


CATEGORY_CHOICES = (
    ('00', 'Fulltime Employee'),
    ('01', 'Parttime Employee'),
    ('02', 'Intern'),
    ('03', 'Contractor'),
    )


OVERTIMEPLAN_CHOICES = (('CB', 'Compensatory Leave'),
                        ('LP', 'Leave Pay'))

LATE_EARLY_CHOICES = ()

OFFDAY1_CHOICES = (
    ('00', 'Sunday'),
    ('01', 'Monday'),
    ('02', 'Tuesday'),
    ('03', 'Wednesday'),
    ('04', 'Thursday'),
    ('05', 'Friday'),
    ('06', 'Saturday'),
    ('07', 'Nothing'),
    )

OFFDAY2_CHOICES = (
    ('00', 'Sunday'),
    ('01', 'Monday'),
    ('02', 'Tuesday'),
    ('03', 'Wednesday'),
    ('04', 'Thursday'),
    ('05', 'Friday'),
    ('06', 'Saturday'),
    ('07', 'Nothing'),
    )

APPLY_CHOICES = (
    ('00', 'All WeekOffs'),
    ('01', 'Odd WeekOffs'),
    ('02', 'Even WeekOffs'),
    ('03', 'Not Applicable'),
    )

RELATION_CHOICES = (
    ('00', 'Father'),
    ('01', 'Mother'),
    ('02', 'Spouse'),
    ('03', 'Child1'),
    ('04', 'Child2'),
    )

BUSI_UNIT_CODE_CHOICES = ()

EMP_STATUS_CHOICES = (
    ('00', 'InActive'),
    ('01', 'Active'),
    )


class OfficeLocation(models.Model):
    name = models.CharField(
        verbose_name="Location Name",
        max_length=30,
        blank=False)
    city = models.CharField("City", max_length=15, blank=False)
    state = models.CharField("State", max_length=20, blank=False)
    zipcode = models.CharField("ZIP Code", max_length=6, blank=False)
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

class Designation(models.Model):
    name = models.CharField(
        verbose_name="Designation Title",
        max_length=40,
        blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class PreviousEmployment(models.Model):
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
        return self.company_name


class EmpAddress(models.Model):
    address1 = models.CharField(
        verbose_name="Address 1",
        max_length=30,
        blank=False)
    address2 = models.CharField(
        verbose_name="Address 2",
        max_length=30,
        blank=False)
    city = models.CharField("City", max_length=15, blank=False)
    state = models.CharField("State", max_length=20, blank=False)
    zipcode = models.CharField("Zip Code", max_length=6, blank=False)

    def __unicode__(self):
        return '{0},{1},{2},{3},{4}'.format(
            self.address1,
            self.address2,
            self.city,
            self.state,
            self.pincode)

""" This class is an extension of the Django user class.  The fields in the
User model can be found here.
https://docs.djangoproject.com/en/dev/ref/contrib/auth/ """


class Employee(models.Model):
    user = models.OneToOneField(User, verbose_name="User")
    middle_name = models.CharField("Middle Name", max_length=15, blank=True)
    employee_assigned_id = models.CharField(
        "Employee ID Assigned",
        max_length=8,
        primary_key=True,
        blank=False)
    idcard = models.CharField(
        "ID Card Identifier",
        max_length=15,
        unique=True,
        blank=False)
    location = models.ForeignKey(OfficeLocation)
    permanent_address = models.ForeignKey(
        EmpAddress,
        verbose_name="Permanent Address",
        related_name="permanent_addr")
    temporary_address = models.ForeignKey(
        EmpAddress,
        verbose_name="Temporary Address",
        related_name="temporary_addr")
    gender = models.CharField(
        "Gender",
        max_length=15,
        choices=GENDER_CHOICES,
        blank=False)
    date_of_birth = models.DateField("Date of Birth", blank=False)
    # Can we make this a choice field?
    nationality = models.CharField("Nationality", max_length=30, blank=False)
    marital_status = models.CharField(
        "Marital Status",
        max_length=10,
        choices=MARITAL_CHOICES,
        blank=False)
    blood_group = models.CharField(
        "Blood Group",
        max_length=3,
        choices=BLOOD_GROUP_CHOICES,
        blank=True)
    division = models.ForeignKey(Division)
    category = models.CharField(
        "Employment Category",
        max_length=3,
        choices=CATEGORY_CHOICES,
        blank=False)
    designation = models.ForeignKey(Designation)
    exprience = models.IntegerField(
        "Experience in Months",
        max_length=3,
        blank=False)
    mobile_phone = models.CharField(
        "Mobile Phone",
        max_length=15,
        unique=True,
        blank=True)
    land_phone = models.CharField("Landline Number", max_length=15, blank=True)
    emergency_phone = models.CharField(
        "Emergency Contact Number",
        max_length=15,
        unique=True,
        blank=False)
    personal_email = models.EmailField(
        "Personal E-mail",
        max_length=250,
        blank=False,
        unique=True)
    PAN = models.CharField(
        "PAN Number",
        max_length=10,
        blank=False,
        unique=True)
    passport_number = models.CharField(
        "Passport Number",
        max_length=10,
        unique=True)
    pf_number = models.CharField(
        "Provide Fund Number",
        max_length=14,
        blank=True)

    previous_employment = models.ManyToManyField(PreviousEmployment)

    probation_end_date = models.DateField("Probation End Date", blank=False)
    confirmation_date = models.DateField("Confirmation Date", blank=False)
    join_date = models.DateField("Joining Date", blank=False)
    resignation_date = models.DateField("Resignation Date")
    exit_date = models.DateField("Exit Date")
    apply_to = models.CharField(
        "Apply To",
        max_length=50,
        choices=APPLY_CHOICES,
        blank=False)
    business_unit = models.ForeignKey(BusinessUnit)
    bank_name = models.CharField("Bank Name", max_length=70, blank=False)
    bank_branch = models.CharField("Bank Branch", max_length=70, blank=False)
    bank_acccount = models.IntegerField(
        "Bank Ac/No",
        max_length=30,
        blank=False,
        unique=True)
    bank_ifsc_code = models.CharField("IFSC Code", max_length=30, blank=False)
    group_insurance_no = models.CharField(
        "Group Insurance Number",
        max_length=30,
        blank=False)
    status = models.CharField(
        "Employee Status",
        max_length=30,
        choices=EMP_STATUS_CHOICES,
        blank=False)
    esi_number = models.CharField("ESI Number", max_length=30)
    photo = models.ImageField(storage=fs, verbose_name="Employee Photo")

    def __unicode__(self):
        return '{0},{1},{2}'.format(
            self.emp_id,
            self.first_name,
            self.last_name)


class FamilyMember(models.Model):
    employee = models.ForeignKey(Employee)
    name = models.CharField("Name", max_length=50, blank=False)
    dob = models.DateField("DOB", blank=False)
    rela_type = models.CharField(
        "Relation Type",
        max_length=50,
        choices=RELATION_CHOICES,
        blank=False)

    def __unicode__(self):
        return (self.name, self.dob)


class Education(models.Model):
    employee = models.ForeignKey(Employee)
    name = models.CharField("Degree", max_length=50, blank=False)
    from_date = models.DateField("From Date", blank=False)
    to_date = models.DateField("To Date", blank=False)
    institute = models.CharField("Institute Name", max_length=50, blank=False)
    overall_marks = models.IntegerField(
        "Total Score/GPA",
        max_length=50,
        blank=False)

    def __unicode__(self):
        return '{0},{1},{2},{3},{4}'.format(
            self.degree,
            self.from_date,
            self.to_date,
            self.institute,
            self.overall_marks)
