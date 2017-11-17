import logging
logger = logging.getLogger('MyANSRSource')
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import CompanyMaster
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from CompanyMaster.models import UpdateDate
import datetime, os
from django.core.validators import URLValidator
from CompanyMaster.models import Practice, SubPractice, DataPoint
from django.core.files.storage import FileSystemStorage
from datetime import date
import Invoice

STARTDATE = (
    ('Data entry error','Data Entry Error'),
)

ENDDATE = (
    ('Data entry error','Data Entry Error'),
    ('Scope change','Scope Change'),
    ('Client requested','Client Requested'),
    ('Ansr renegotiated date','Ansr Renegotiated Date'),
    ('Client Feeback','Client Feeback'),
    ('Material Delay','Material Delay'),
    ('SME Unavailability','SME Unavailability'),
    ('Quality Issues','Quality Issues'),
    ('Productivity Issues','Productivity Issues'),
    ('Estimation Issues','Estimation Issues'),
)

EFFORT = (
    ('Data entry error','Data Entry Error'),
    ('Scope change','Scope Change'),
    ('Project effort confirmed post sample','Project effort confirmed post sample'),
)

AMOUNT = (
    ('Data entry error','Data Entry Error'),
    ('Scope change','Scope Change'),
    ('Project value confirmed','Project value confirmed'),
    ('Project Value Changed based on actuals','Project Value Changed based on actuals'),
)

CLOSE = (
    ('Project completed','Project completed'),
    ('project cancelled','Project Cancelled'),
)


TASKTYPEFLAG = (
    ('B', 'Revenue'),
    ('I', 'Idle'),
    ('N', 'Non-Revenue'),
)
FREQUENCY = (
    ('M', 'Monthly'),
    ('W', 'Weekly'),
)
REPORTNAME = (
    ('nonclosedprojectts', 'Non Closed Project TS'),
)

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday']

alphanumeric = RegexValidator(r'^[0-9a-zA-Z-]*$',
                              'Only alphanumeric characters are allowed.')

PROJECTFINTYPE = (
    ('FP', 'Fixed Price'),
    ('T&M', 'T&M')
)
APRROVECHOICES = (
    ('0', 'ACTIVE'),
    ('1', 'APPROVED'),
    ('2','REJECTED')
)


ROLE = (
    ('developer', 'Developer'),
    ('copy editor', 'Copy Editor'),
    ('reviewer','Reviewer'),
    ('delivery manager', 'Delivery Manager')
)
TEAM_CHOICES = (('0', 'assessment'), ('1', 'learning'))
PROJECT_FUNDING = (('Customer Paid','Customer Paid'),
                   ('Demo/Pilot/POC', 'Demo/Pilot/POC'),
                   ('Operations', 'Operations'),
                   ('Bench', 'Bench'))
#upload path for sow and estimation


def change_file_path(instance, filename):
    ''' This function generates a random string of length 16 which will be a combination of (4 digits + 4
    characters(lowercase) + 4 digits + 4 characters(uppercase)) seperated 4 characters by hyphen(-) '''

    import random
    import string

    # random_str length will be 16 which will be combination of (4 digits + 4 characters + 4 digits + 4 characters)
    random_str = "".join([random.choice(string.uppercase) for i in range(0, 4)]) + "".join(
        [random.choice(string.digits) for i in range(0, 4)]) + \
                 "".join([random.choice(string.lowercase) for i in range(0, 4)]) + "".join(
        [random.choice(string.digits) for i in range(0, 4)])

    # return string seperated by hyphen eg:
    random_str = random_str[:4] + "-" + random_str[4:8] + "-" + random_str[8:12] + "-" + random_str[12:]
    filetype = filename.split(".")[-1].lower()
    filename = random_str + "." + filetype
    path = "MyANSRSource/uploads/" + str(datetime.datetime.now().year) + "/" + str(
        datetime.datetime.now().month) + "/" + str(datetime.datetime.now().day) + "/"
    os_path = os.path.join(path, filename)
    return os_path


class TimeStampAbstractModel(models.Model):
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True,)
    created_by = models.ForeignKey(User, related_name='%(class)s_created_by',  default=35)
    updated_on = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_by = models.ForeignKey(User, related_name='%(class)s_updated_by', blank=True, null=True,  default=35)

    class Meta:
        abstract = True


class Role(TimeStampAbstractModel):
    role = models.CharField(verbose_name='Role', choices=ROLE, max_length=20,)
    is_active = models.BooleanField(verbose_name='Active', default=True)

    def __unicode__(self):
        return self.role


class Product(TimeStampAbstractModel):
    name = models.CharField(verbose_name='Product name',max_length=50,)
    is_active = models.BooleanField(verbose_name='Active', default=True)
    unit = models.CharField(verbose_name='Product unit', max_length=50, )

    def __unicode__(self):
        return self.name + ' | ' + self.unit


class Book(models.Model):
    name = models.CharField(max_length=100, null=False,
                            verbose_name="Name")
    author = models.CharField(max_length=100, null=False,
                              verbose_name="Author")
    edition = models.CharField(max_length=30, null=True, blank=True)
    isbn = models.CharField(max_length=13,
                               blank=True, null=True,
                               verbose_name="ISBN")
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?"
    )
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return u'{0}|{1}|{2}'.format(self.author, self.edition, self.name)

    class Meta:
        unique_together = ('name', 'edition', 'author', )


class Activity(models.Model):
    name = models.CharField(max_length=100, null=False,
                            verbose_name="Activity")
    code = models.CharField(max_length=1, null=False, unique=True,
                            verbose_name="Short Code", default=None)
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?"
    )
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = 'Activity'
        verbose_name_plural = 'Activities'


class projectType(models.Model):
    code = models.CharField(max_length=2, null=False,
                            verbose_name="Unit of Work")
    description = models.CharField(max_length=100, null=False,
                                   verbose_name="Description")
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.description


class Task(models.Model):
    projectType = models.ForeignKey(projectType, verbose_name="Project Type")
    name = models.CharField(max_length=100, verbose_name="Task")
    code = models.CharField(max_length=1, null=False,
                            verbose_name="Short Code", default=None)
    taskType = models.CharField(max_length=2,
                                choices=TASKTYPEFLAG,
                                verbose_name='Task type',
                                default=None)
    norm = models.DecimalField(
        default=0.0,
        max_digits=12,
        decimal_places=2,
        verbose_name="Norm",
        validators=[MinValueValidator(0.0)]
    )
    active = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Is Active?")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = (('projectType', 'code'), ('projectType', 'name'))


class Chapter(models.Model):
    book = models.ForeignKey(Book)
    name = models.CharField(max_length=100, verbose_name="Name")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class ProjectSopTemplate(models.Model):
    name = models.CharField(max_length=120, verbose_name='process Template name')
    actual_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(blank=False, default=True, verbose_name='Active or not')
    created_by = models.ForeignKey(User)
    created_at = models.DateTimeField(verbose_name='Created at', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='updated at', auto_now_add=True)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name = 'Project Process Template'


class qualitysop(models.Model):
    name = models.CharField(verbose_name="Quality SOP Name", max_length=200, )
    SOPlink = models.TextField(validators=[URLValidator()])
    product_type = models.CharField(max_length=50, blank=True, null=True, choices=TEAM_CHOICES, verbose_name="Product",
                                    default=TEAM_CHOICES[0][0])
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return unicode(self.name)

    class Meta:
        verbose_name = 'Quality SOP Table'


class ProjectScope(models.Model):
    scope = models.CharField(verbose_name="Project scope Name", max_length=200)
    IsActive = models.BooleanField(verbose_name="Active")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return unicode(self.scope)

    class Meta:
        verbose_name = "Project Scope Table"


class ProjectAsset(models.Model):
    Asset = models.CharField(verbose_name="Project Asset", max_length=200)
    Is_Active = models.BooleanField(verbose_name="Active")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    created_by = models.ForeignKey(User)

    def __unicode__(self):
        return self.Asset

    class Meta:
        verbose_name = "Project Asset Table"


class Project(models.Model):
    projectType = models.ForeignKey(
        projectType,
        null=False,
        verbose_name="Project Type"
    )
    name = models.CharField(max_length=50,
                            verbose_name="Project Name",
                            unique=True)
    customerContact = models.CharField(
        max_length=100,
        default=None,
        verbose_name="Customer Contact",
        # related_name="Cusomer Contact"
    )
    bu = models.ForeignKey(
        CompanyMaster.models.BusinessUnit,
        verbose_name="Business Unit"
    )
    customer = models.ForeignKey(
        CompanyMaster.models.Customer,
        verbose_name="Customer",
        default=None,
        null=False,
    )
    currentProject = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="New Development"
    )
    signed = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Contract Signed"
    )
    internal = models.BooleanField(
        blank=False,
        default=False,
        null=False,
        verbose_name="Internal Project"
    )
    projectId = models.CharField(
        max_length=60,
        null=False,
        unique=True,
        verbose_name='Project Code')
    po = models.CharField(max_length=60, null=False,
                          blank=False, default=0,
                          verbose_name="P.O.", validators=[alphanumeric])
    startDate = models.DateField(verbose_name="Project Start Date",
                                 default=timezone.now)
    endDate = models.DateField(verbose_name="Project End Date",
                               default=timezone.now)
    salesForceNumber = models.IntegerField(default=0, help_text="8 digit number starting with 201",
                                           verbose_name="SF\
                                           Opportunity Number",
                                           validators=[MinValueValidator(20100000), MaxValueValidator(99999999)])
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name=" Total Planned Effort",
                                        validators=[MinValueValidator(8)])
    contingencyEffort = models.IntegerField(default=0,
                                            blank=True,
                                            null=True,
                                            verbose_name="Contigency Effort",
                                            validators=[MinValueValidator(0)])
    projectManager = models.ManyToManyField(User,
                                            through='ProjectManager',
                                            verbose_name="Additional Manager")
    # Chapters to be worked on in the project
    book = models.ForeignKey(Book,
                             verbose_name="Book/Title",
                             default=None,
                             null=False
                             )
    totalValue = models.DecimalField(default=0.0,
                                     max_digits=12,
                                     decimal_places=2,
                                     verbose_name="Project Value",
                                     validators=[MinValueValidator(0.0)])
    closed = models.BooleanField(
        default=False,
        null=False,
        verbose_name="Project Closed"
    )
    remark = models.CharField(verbose_name="Project Rejection message", null=True, blank=True, default='Nothing', max_length=100)
    active = models.BooleanField(verbose_name="Is Active", default=False)
    rejected = models.BooleanField(verbose_name="Rejected or not", default=False)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.projectId + u' : ' + self.name

    class Meta:
        permissions = (
            ("create_project", 'Create ANSR projects'),
            ("manage_project", "Manage ANSR Project"),
            ("approve_timesheet", "Approve timesheets"),
            ("manage_milestones", "Manage Project Milestones"),
            ("view_all_projects", "View all projects"),
            ("view_all_reports", "View All Reports"),
            )


class ProjectDetail(models.Model):
    project = models.OneToOneField(Project, related_name='project_detail_project')
    projecttemplate = models.ForeignKey(ProjectSopTemplate, null=True, blank=True)
    Discipline = models.ForeignKey(DataPoint, verbose_name='Discipline Name', null=True, blank=True)
    projectFinType = models.CharField(verbose_name='Project Finance Type ', choices=PROJECTFINTYPE, max_length=20,
                                      blank=True, null=True)
    portfolio_manager = models.ForeignKey(User, verbose_name='Portfolio Manager', related_name='portfolio_manager', default=35,null=True,blank=True)
    deliveryManager = models.ForeignKey(User, verbose_name='Project Delievery Manager')
    Sowdocument = models.FileField(upload_to=change_file_path, blank=True, null=True, verbose_name="Upload Project SOW")
    Estimationdocument = models.FileField(upload_to=change_file_path, blank=True, null=True,
                                          verbose_name="Upload project Estimation Document")
    Project_funding = models.CharField(verbose_name='Funding TYpe', choices=PROJECT_FUNDING, max_length=15, null=True, blank=True,)
    SOP = models.ForeignKey(qualitysop, verbose_name='Quality Sop ID', null=True, blank=True)
    Scope = models.ForeignKey(ProjectScope, verbose_name='Project Scope ID', null=True, blank=True)
    Asset = models.ForeignKey(ProjectAsset, verbose_name='Project Asset ID', null=True, blank=True)
    outsource_contract_value = models.DecimalField(default=0.0,
                                                   max_digits=12,
                                                   decimal_places=2,
                                                   verbose_name="Outsource Contract Value",
                                                   validators=[MinValueValidator(0.0)])
    pmDelegate = models.ForeignKey(User, verbose_name="PM Delegate", related_name='pmDelegate', default=None,
                                   null=True, blank=True)

    def __unicode__(self):
        return self.project.projectId + u' : ' + self.project.name

    class Meta:
        verbose_name = "Project Additional Detail Table"


class ProjectManager(models.Model):
    # Creating Explicit M2M, to copy existing FK to M2M
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)


class TimeSheetEntry(models.Model):
    project = models.ForeignKey(Project, blank=False,
                                verbose_name="Project Name", null=True)
    # Week details
    wkstart = models.DateField(default=None, blank=True,
                               verbose_name="Week Start")
    wkend = models.DateField(default=None, blank=True, verbose_name="Week End")

    location = models.ForeignKey(
        CompanyMaster.models.OfficeLocation,
        verbose_name="Location",
        null=True
    )
    chapter = models.ForeignKey(Chapter, blank=False,
                                verbose_name="Chapter/Subtitle", null=True)
    activity = models.ForeignKey(Activity, blank=False,
                                 verbose_name="Activity", null=True)
    task = models.ForeignKey(Task, blank=False,
                             verbose_name="Task", null=True)
    # Effort capture
    mondayQ = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Mon")
    mondayH = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Mon")
    tuesdayQ = models.DecimalField(default=0.0, max_digits=12,
                                   decimal_places=2, verbose_name="Tue")
    tuesdayH = models.DecimalField(default=0.0, max_digits=12,
                                   decimal_places=2, verbose_name="Tue")
    wednesdayQ = models.DecimalField(default=0.0, max_digits=12,
                                     decimal_places=2, verbose_name="Wed")
    wednesdayH = models.DecimalField(default=0.0, max_digits=12,
                                     decimal_places=2, verbose_name="Wed")
    thursdayQ = models.DecimalField(default=0.0, max_digits=12,
                                    decimal_places=2, verbose_name="Thu")
    thursdayH = models.DecimalField(default=0.0, max_digits=12,
                                    decimal_places=2, verbose_name="Thu")
    fridayQ = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Fri")
    fridayH = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Fri")
    saturdayQ = models.DecimalField(default=0.0, max_digits=12,
                                    decimal_places=2, verbose_name="Sat")
    saturdayH = models.DecimalField(default=0.0, max_digits=12,
                                    decimal_places=2, verbose_name="Sat")
    sundayQ = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Sun")
    sundayH = models.DecimalField(default=0.0, max_digits=12,
                                  decimal_places=2, verbose_name="Sun")
    totalQ = models.DecimalField(default=0.0, max_digits=12,
                                 decimal_places=2, verbose_name="Total")
    totalH = models.DecimalField(default=0.0, max_digits=12,
                                 decimal_places=2, verbose_name="Total")
    approved = models.BooleanField(default=False)
    hold = models.BooleanField(default=False)

    # Approval related details
    approvedon = models.DateTimeField(default=None, null=True, blank=True,
                                      verbose_name="Approved On",
                                      editable=False)
    managerFeedback = models.CharField(default=None, null=True, blank=True,
                                       max_length=1000,
                                       verbose_name="Manager Feedback")
    remarks = models.CharField(default=None, null=True, blank=True, max_length=255,  verbose_name="Employee Remarks")

    teamMember = models.ForeignKey(User, editable=False)
    exception = models.CharField(default="No Exception", max_length=75)
    billable = models.BooleanField(default=False, verbose_name="Billable")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    class Meta:
        verbose_name = 'Timesheet Entry'
        verbose_name_plural = 'Timesheet Entries'
        permissions = (
            ("enter_timesheet", "Allow timetracking"),
            )


class MilestoneType(models.Model):
    milestone_type = models.CharField(max_length=50, verbose_name="Milestone Type")
    is_financial = models.BooleanField(default=False, verbose_name="Is Financial")
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.milestone_type

    class Meta:
        verbose_name = "Milestone Type"
        verbose_name_plural = "Milestone Types"


class Milestone(UpdateDate):
    milestone_type = models.ForeignKey(MilestoneType)
    name = models.CharField(default=None, blank=False, max_length=100,
                            null=True, verbose_name="name")
    is_final_milestone = models.BooleanField(verbose_name="Is Final Milestone", default=False)
    check_schedule_deviation = models.BooleanField(verbose_name="Check Schedule Deviation", default=False)
    is_active = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Project Milestones"
        verbose_name = "Project Milestone"


class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project)
    milestoneDate = models.DateField(verbose_name="Milestone Date",
                                     default=timezone.now)
    description = models.CharField(default=None, blank=False, max_length=1000,
                                   null=True, verbose_name="Description")
    name = models.ForeignKey(Milestone, default=None, verbose_name="Milestone Name", null=True)
    unit = models.IntegerField(verbose_name="Unit",blank=True, null=True, default= 0.0)
    rate_per_unit = models.DecimalField(verbose_name="Rate per Unit", blank=True, null=True, default= 0.0, max_digits=20, decimal_places=2)
    amount = models.DecimalField(default=0.0,
                                 max_digits=12,
                                 decimal_places=2,
                                 verbose_name="Amount")
    closed = models.BooleanField(
        default=False,
        null=False,
        blank=False,
        verbose_name="Completed"
    )
    closedon = models.DateTimeField(default=None, null=True, blank=True,
                                    verbose_name="Closed On",
                                    editable=False)
    financial = models.BooleanField(default=False,
                                    verbose_name="Deviation",
                                    blank=False,
                                    null=False
                                    )
    reason = models.CharField(default=None, blank=True, max_length=100,
                              verbose_name="Reason for change", null=True)
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def save(self, request=None):
        used_user = request.user if request else User.objects.get(id=35)
        if self.closed and self.financial:
            Invoice.models.Invoice.objects.get_or_create(
                project=self.project,
                milestone_date=self.milestoneDate,
                milestone_name=self.description,
                description=self.description,
                closed_on_date=date.today(),
                amount=self.amount,
                user=used_user
            )

        super(ProjectMilestone, self).save()


class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project,related_name="project_team_member_project")
    member = models.ForeignKey(User, blank=True, null=True)
    product = models.ForeignKey(Product, blank=True, null=True)
    role = models.ForeignKey(Role, blank=True,null= True)
    startDate = models.DateField(verbose_name='Start date on project',
                                 blank=True,
                                 default=timezone.now)
    endDate = models.DateField(verbose_name='End date on project',
                               blank=True,
                               default=timezone.now)
    plannedEffort = models.DecimalField(default=0,
                                        max_digits=12,
                                        blank=True,
                                        decimal_places=2,
                                        verbose_name="Planned Effort")
    plannedcount = models.IntegerField(default=0, verbose_name="planned count", blank=True)
    actualcount = models.IntegerField(default=0, verbose_name="actual count", blank=True)
    active = models.BooleanField(default=True)
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.member)


class ProjectChangeInfo(models.Model):
    # project change Request Fields
    project = models.ForeignKey(Project, verbose_name="Project Name")
    crId = models.CharField(default=None, blank=True, null=True,
                            max_length=100, verbose_name="Change Request ID")
    reason = models.CharField(max_length=100, default=0, blank=True,
                              null=True,
                              verbose_name="Reason for change")
    startdate_dropdown = models.CharField(choices=STARTDATE, max_length=100, blank=True, null=True, default=None)
    enddate_dropdown = models.CharField(choices=ENDDATE, max_length=100, blank=True, null=True, default=None)
    effort_dropdown = models.CharField(choices=EFFORT, max_length=100, blank=True, null=True, default=None)
    amount_dropdown = models.CharField(choices=AMOUNT, max_length=100, blank=True, null=True, default=None)
    close_dropdown = models.CharField(choices=CLOSE, max_length=100, blank=True, null=True, default=None)
    salesForceNumber = models.IntegerField(default=0, blank=True, null=True,
                                           help_text="8 digit number starting with 201",
                                           verbose_name="SF\
                                                       Opportunity Number",
                                           validators=[MinValueValidator(20100000), MaxValueValidator(99999999)])
    customerContact = models.CharField(
        max_length=100,
        default=None,
        verbose_name="Customer Contact",
        blank=True,
        null=True
        # related_name="Cusomer Contact"
    )
    endDate = models.DateField(verbose_name="Revised Project End Date",
                               default=None, blank=False, null=False)
    # po = models.CharField(max_length=60, null=False,
    #                       blank=False, default=0,
    #                       verbose_name="P.O.", validators=[alphanumeric])
    revisedEffort = models.IntegerField(default=0,
                                        validators=[MinValueValidator(0)],
                                        verbose_name="Revised Effort")
    revisedTotal = models.DecimalField(default=0.0,
                                       max_digits=12,
                                       validators=[MinValueValidator(0)],
                                       decimal_places=2,
                                       verbose_name="Revised amount")
    closed = models.BooleanField(default=False,
                                 verbose_name="Close the Project")
    closedOn = models.DateTimeField(default=None, blank=True, null=True)
    signed = models.BooleanField(default=False,
                                 verbose_name="Contract Signed")
    # Record Entered / Updated Date
    #New Model Field As per New Project Creation Screen
    startDate = models.DateField(verbose_name="Revised Project Start Date", blank=True, null=True)
    bu = models.ForeignKey(CompanyMaster.models.BusinessUnit, verbose_name="Business Unit", default=None,blank=True, null=True)
    Sowdocument = models.FileField(upload_to=change_file_path, blank=True, null=True, verbose_name="Upload Project SOW")
    estimationDocument = models.FileField(upload_to=change_file_path, blank=True, null=True, verbose_name="Upload Estimation Document")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
    approved = models.CharField(verbose_name="Approved", choices=APRROVECHOICES, default=0, max_length=1)

    def __unicode__(self):
        return self.crId


class Report(models.Model):
    name = models.CharField(max_length=50,
                            choices=REPORTNAME,
                            verbose_name='Report',
                            default='nonclosedprojectts')
    notify = models.ManyToManyField(User, verbose_name="Notifier(s)")
    freq = models.CharField(max_length=2,
                            choices=FREQUENCY,
                            verbose_name='Frequency',
                            default='W')
    day = models.IntegerField(choices=[
                                  (k, v) for k, v in enumerate(
                                      [i for i in xrange(1, 31)])
                              ],
                              verbose_name='Day',
                              default=0)
    weekday = models.IntegerField(choices=[(k, v) for k, v in enumerate(days)],
                                  verbose_name='Weekday',
                                  default=0)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class BTGReport(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project Name")
    member = models.ForeignKey(User)
    btg = models.IntegerField(default=0, verbose_name="BTG",
                              validators=[MinValueValidator(0)])
    btgMonth = models.IntegerField(default=1, verbose_name="BTG",
                                   validators=[MinValueValidator(1)])
    btgYear = models.IntegerField(default=1990, verbose_name="BTG",
                                  validators=[MinValueValidator(1990)])
    currMonthRR = models.IntegerField(default=0,
                                      validators=[MinValueValidator(0)])
    currMonthIN = models.IntegerField(default=0,
                                      validators=[MinValueValidator(0)],
                                      verbose_name="Number Of Invoices")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.project


class SendEmail(models.Model):
    toAddr = models.CharField(default=None, null=False, max_length=1000)
    template_name = models.CharField(default=None, null=False, max_length=100)
    content = models.CharField(default=None, null=False, max_length=1000)
    sent = models.BooleanField(default=False)
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
