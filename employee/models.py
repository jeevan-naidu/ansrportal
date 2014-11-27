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

B_GROUP_CHOICES = (
    ('00', 'A+'),
    ('01', 'A-'),
    ('02', 'B+'),
    ('03', 'B-'),
    ('04', 'O+'),
    ('05', 'O-'),
    ('06', 'AB+'),
    ('07', 'AB-'),
    )

DEPARTMENT_CHOICES = (
    ('Authoring', (
        ('00', 'Production'),
        ('01', 'Marketing & Sales'),
        ('02', 'Finance'),
        )
     ),
    ('Multimedia', (
        ('03', 'Human resource'),
        ('04', 'IT Department'),
        )
     )
    )

CATEGORY_CHOICES = (
    ('00', 'Fulltime Employee'),
    ('01', 'Parttime Employee'),
    ('02', 'Intern'),
    ('03', 'Contractor'),
    )

DESIGNATION_CHOICES = (
    ('00', 'Developer D1'),
    ('01', 'Developer D2'),
    ('02', 'Quality Analyst'),
    ('03', 'Copy Editor'),
    ('04', 'EA'),
    )

SHIFT_CHOICES = (
    ('00', 'General Shift'),
    ('01', 'A Shift'),
    ('02', 'B Shift'),
    )

LEAVE_CHOICES = (
    ('00', 'Permission'),
    ('01', 'Without Persmission'),
    )

ATTEN_CHOICES = (
    ('00', 'First Off'),
    ('01', 'Last Off'),
    ('02', 'Entire Off'),
    )

OVER_TPLAN_CHOICES = ()

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


class Locations(models.Model):
    name = models.CharField(
        verbose_name="Location Name",
        max_length=30,
        blank=False)
    city = models.CharField("City", max_length=15, blank=False)
    state = models.CharField("State", max_length=20, blank=False)
    zipcode = models.CharField("ZIP Code", max_length=6, blank=False)


# Create your models here.


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

""" This class is an extension of the Django user class.  The fields in the User
 model can be found here.
 https://docs.djangoproject.com/en/dev/ref/contrib/auth/
 """


class Employee(models.Model):
    user = models.OneToOneField(User, verbose_name="User")
    middle_name = models.CharField("Middle Name", max_length=15, blank=True)
    employee_assigned_id = models.CharField(
        "Employee ID Assigned",
        max_length=8,
        primary_key=True,
        blank=False)
    idcard = models.CharField(
        "Card ID",
        max_length=8,
        unique=True,
        blank=False)
    location = models.ForeignKey(Locations)
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
    d_o_b = models.DateField("Date of Birth", blank=False)
    # Can we make this a choice field?
    nationality = models.CharField("Nationality", max_length=30, blank=False)
    marital_status = models.CharField(
        "Marital Status",
        max_length=10,
        choices=MARITAL_CHOICES,
        blank=False)
    blood_grop = models.CharField(
        "Blood Group",
        max_length=50,
        choices=B_GROUP_CHOICES,
        blank=False)
    depar_code = models.CharField(
        "Department Code",
        max_length=50,
        choices=DEPARTMENT_CHOICES,
        blank=False)
    cate_code = models.CharField(
        "Category Code",
        max_length=50,
        choices=CATEGORY_CHOICES,
        blank=False)
    desig_code = models.CharField(
        "Designation Code",
        max_length=50,
        choices=DESIGNATION_CHOICES,
        blank=False)
    year_exp = models.IntegerField(
        "Years of Experience",
        max_length=2,
        blank=False)
    mob_num = models.CharField(
        "Mobile Number",
        max_length=15,
        unique=True,
        blank=False)
    land_num = models.CharField("Landline Number", max_length=15)
    emer_num = models.CharField(
        "Emergency Contact Number",
        max_length=15,
        unique=True,
        blank=False)
    personal_email = models.EmailField(
        "Personal E-mail",
        max_length=250,
        blank=False,
        unique=True)
    official_email = models.EmailField(
        "Official E-mail",
        max_length=250,
        blank=False,
        unique=True)
    pan_no = models.CharField(
        "PAN No",
        max_length=10,
        blank=False,
        unique=True)
    passport_no = models.CharField("Passport No", max_length=10, unique=True)
    pf_no = models.CharField("PF No", max_length=14,  blank=False)
    prev_comp_name = models.CharField("Previous Company Name", max_length=150)
    prev_comp_addr = models.CharField(
        "Previous Company Address",
        max_length=500)
    prev_comp_duration = models.IntegerField(
        "Previous Company Duration",
        max_length=3,
        help_text="Duration should be a month")
    prev_comp_pf = models.CharField("Previous Company PF No", max_length=15)
    prev_comp_ctc = models.DecimalField(
        "Previous Company CTC",
        max_digits=15,
        decimal_places=2)
    prev_leav_date = models.DateField("Previous Leaving Date")
    prev_reas_leav = models.CharField(
        "Reason for Leaving in previous company",
        max_length=250)
    shift_plan = models.CharField(
        "Shift Plan",
        max_length=15,
        choices=SHIFT_CHOICES,
        blank=False)
    leave_plan = models.CharField(
        "Leave Plan",
        max_length=50,
        choices=LEAVE_CHOICES,
        blank=False)
    att_plan = models.CharField(
        "Attendance Plan",
        max_length=50,
        choices=ATTEN_CHOICES,
        blank=False)
    over_tplan = models.CharField(
        "OverTime Plan",
        max_length=50,
        choices=OVER_TPLAN_CHOICES,
        blank=False)
    lat_early_plan = models.CharField(
        "Late/Early Plan",
        max_length=15,
        choices=LATE_EARLY_CHOICES,
        blank=False)
    prob_date = models.DateField("Probation Date", blank=False)
    confirm_date = models.DateField("Confirm Date", blank=False)
    join_date = models.DateField("Joining Date", blank=False)
    res_date = models.DateField("Designation Date")
    exit_date = models.DateField("Exit Date")
    bus_route = models.CharField("Bus Route", max_length=15)
    off_day1 = models.CharField(
        "Off Day1",
        max_length=20,
        choices=OFFDAY1_CHOICES,
        blank=False)
    off_day2 = models.CharField(
        "Off Day2",
        max_length=20,
        choices=OFFDAY2_CHOICES,
        blank=False)
    apply_to = models.CharField(
        "Apply To",
        max_length=50,
        choices=APPLY_CHOICES,
        blank=False)
    busin_unit_code = models.CharField(
        "Business Unit Code",
        max_length=50,
        choices=BUSI_UNIT_CODE_CHOICES,
        blank=False)
    cost_centre = models.CharField("Cost Centre", max_length=10, blank=False)
    bank_name = models.CharField("Bank Name", max_length=70, blank=False)
    bank_branch = models.CharField("Bank Branch", max_length=70, blank=False)
    bank_ac = models.IntegerField(
        "Bank Ac/No",
        max_length=30,
        blank=False,
        unique=True)
    ifsc_code = models.CharField("IFSC Code", max_length=30, blank=False)
    group_insu_no = models.CharField(
        "Group Insurance Number",
        max_length=30,
        blank=False)
    emp_status = models.CharField(
        "Employee Status",
        max_length=30,
        choices=EMP_STATUS_CHOICES,
        blank=False)
    esi_num = models.CharField("ESI Number", max_length=30)
    photo = models.ImageField(storage=fs, verbose_name="Employee Photo")

    def __unicode__(self):
        return '{0},{1},{2}'.format(
            self.emp_id,
            self.first_name,
            self.last_name)


class Relative(models.Model):
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
        "Percentage",
        max_length=50,
        blank=False)

    def __unicode__(self):
        return '{0},{1},{2},{3},{4}'.format(
            self.degree,
            self.from_date,
            self.to_date,
            self.institute,
            self.overall_marks)
