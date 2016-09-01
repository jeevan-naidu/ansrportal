import logging
logger = logging.getLogger('MyANSRSource')
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import CompanyMaster
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator

MEASURE_PRODUCTIVITY_CHOICES = (('yes', 'Yes'), ('no', 'No'))

LINKED_TO_ASSET_CHOICES = (('yes', 'Yes'), ('no', 'No'))

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

class Book(models.Model):
    name = models.CharField(max_length=100, null=False,
                            verbose_name="Name")
    author = models.CharField(max_length=100, null=False,
                              verbose_name="Author")
    edition = models.CharField(max_length=30, null=True, blank=True)
    isbn = models.IntegerField(default=None,
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
    code = models.CharField(max_length=10, null=False,
                            verbose_name="Unit of Work", help_text='max length 10')
    description = models.CharField(max_length=100, null=False,
                                   verbose_name="Description")
    linked_to_asset = models.CharField(max_length=10, choices=LINKED_TO_ASSET_CHOICES, blank=True, null=True)
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
    measure_productivity = models.CharField(max_length=200, choices=MEASURE_PRODUCTIVITY_CHOICES)
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
        blank=True,
        null=True,
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
                                           Oppurtunity Number",
                                           validators=[MinValueValidator(20100000), MaxValueValidator(99999999)])
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort",
                                        validators=[MinValueValidator(0)])
    contingencyEffort = models.IntegerField(default=0,
                                            blank=True,
                                            null=True,
                                            verbose_name="Contigency Effort",
                                            validators=[MinValueValidator(0)])
    projectManager = models.ManyToManyField(User,
                                            through='ProjectManager',
                                            verbose_name="Project Leader")
    # Chapters to be worked on in the project
    book = models.ForeignKey(Book,
                             verbose_name="Book/Title",
                             default=None,
                             null=False
                             )
    totalValue = models.DecimalField(default=0.0,
                                     max_digits=12,
                                     decimal_places=2,
                                     verbose_name="Total Value",
                                     validators=[MinValueValidator(0.0)])
    closed = models.BooleanField(
        default=False,
        null=False,
        verbose_name="Project Closed"
    )
    # Record Entered / Updated Date
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


class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project)
    milestoneDate = models.DateField(verbose_name="Milestone Date",
                                     default=timezone.now)
    description = models.CharField(default=None, blank=False, max_length=1000,
                                   null=True, verbose_name="Description")
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
                                    verbose_name="Financial",
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


class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project)
    member = models.ForeignKey(User, blank=True, null=True)
    datapoint = models.ForeignKey(
        CompanyMaster.models.DataPoint,
        verbose_name=u'Service Line',
        blank=True,
        null=True
    )
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
    rate = models.IntegerField(default=100, verbose_name="%", blank=True)
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
    reason = models.CharField(max_length=100, default=None, blank=False,
                              null=False,
                              verbose_name="Reason for change")
    endDate = models.DateField(verbose_name="Revised Project End Date",
                               default=None, blank=False, null=False)
    po = models.CharField(max_length=60, null=False,
                          blank=False, default=0,
                          verbose_name="P.O.", validators=[alphanumeric])
    revisedEffort = models.IntegerField(default=0,
                                        validators=[MinValueValidator(0)],
                                        verbose_name="Revised Effort")
    revisedTotal = models.DecimalField(default=0.0,
                                       max_digits=12,
                                       validators=[MinValueValidator(0)],
                                       decimal_places=2,
                                       verbose_name="Revised amount")
    salesForceNumber = models.IntegerField(default=0, help_text="8 digit number starting with 201",
                                           verbose_name="Sales Force \
                                           Oppurtunity Number",
                                           validators=[MinValueValidator(20100000), MaxValueValidator(99999999)])
    closed = models.BooleanField(default=False,
                                 verbose_name="Close the Project")
    closedOn = models.DateTimeField(default=None, blank=True, null=True)
    signed = models.BooleanField(default=False,
                                 verbose_name="Contract Signed")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

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
    day = models.IntegerField(max_length=2,
                              choices=[
                                  (k, v) for k, v in enumerate(
                                      [i for i in xrange(1, 31)])
                              ],
                              verbose_name='Day',
                              default=0)
    weekday = models.IntegerField(max_length=2,
                                  choices=[(k, v) for k, v in enumerate(days)],
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
