from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import CompanyMaster
import employee


class Book(models.Model):
    name = models.CharField(max_length=100, null=False,
                            verbose_name="Book Name")
    author = models.CharField(max_length=100, null=False,
                              verbose_name="Author")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class projectType(models.Model):
    code = models.CharField(max_length=2, null=False,
                            verbose_name="Unit of Work")
    description = models.CharField(max_length=100, null=False,
                                   verbose_name="Description")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.description


class Chapter(models.Model):
    book = models.ForeignKey(Book)
    name = models.CharField(max_length=100, verbose_name="Chapter Name")
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
    name = models.CharField(max_length=50, verbose_name="Project Name")
    currentProject = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Project Stage"
    )
    signed = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Contact Signed"
    )
    internal = models.BooleanField(
        blank=False,
        default=False,
        null=False,
        verbose_name="Internal Project"
    )
    projectId = models.CharField(max_length=60, null=False)
    startDate = models.DateField(verbose_name="Project Start Date")
    endDate = models.DateField(verbose_name="Project End Date")
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort")
    contingencyEffort = models.IntegerField(default=0,
                                            verbose_name="Contigency Effort")
    projectManager = models.ForeignKey(User)
    # Chapters to be worked on in the project
    book = models.ForeignKey(Book,
                             verbose_name="Book",
                             default=None,
                             null=False
                             )
    chapters = models.ManyToManyField(Chapter)
    totalValue = models.DecimalField(default=0.0,
                                     max_digits=12,
                                     decimal_places=2,
                                     verbose_name="Total Value")
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
        return unicode(self.name)

    class Meta:
        permissions = (
            ("manage_project", "Create/Manage ANSR Project"),
            ("approve_timesheet", "Approve timesheets"),
            ("manage_milestones", "Manage Project Milestones"),
            )


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
                                verbose_name="Chapter", null=True)
    activity = models.CharField(max_length=2, null=True)
    task = models.CharField(null=True, max_length=2)
    # Effort capture
    mondayQ = models.IntegerField(default=0, verbose_name="Mon")
    mondayH = models.IntegerField(default=0, verbose_name="Mon")
    tuesdayQ = models.IntegerField(default=0, verbose_name="Tue")
    tuesdayH = models.IntegerField(default=0, verbose_name="Tue")
    wednesdayQ = models.IntegerField(default=0, verbose_name="Wed")
    wednesdayH = models.IntegerField(default=0, verbose_name="Wed")
    thursdayQ = models.IntegerField(default=0, verbose_name="Thu")
    thursdayH = models.IntegerField(default=0, verbose_name="Thu")
    fridayQ = models.IntegerField(default=0, verbose_name="Fri")
    fridayH = models.IntegerField(default=0, verbose_name="Fri")
    saturdayQ = models.IntegerField(default=0, verbose_name="Sat")
    saturdayH = models.IntegerField(default=0, verbose_name="Sat")
    sundayQ = models.IntegerField(default=0, verbose_name="Sun")
    sundayH = models.IntegerField(default=0, verbose_name="Sun")
    totalQ = models.IntegerField(default=0, verbose_name="Total")
    totalH = models.IntegerField(default=0, verbose_name="Total")
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
    reason = models.CharField(default=None, blank=True, max_length=100,
                              verbose_name="Reason for change", null=True)
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project)
    member = models.ForeignKey(User)
    role = models.ForeignKey(
        employee.models.Designation,
        verbose_name="Role",
        default=None,
        null=False,
    )
    startDate = models.DateField(verbose_name='Start date on project',
                                 default=timezone.now)
    endDate = models.DateField(verbose_name='End date on project',
                               default=timezone.now)
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort")
    rate = models.IntegerField(default=100, verbose_name="%")
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
    reason = models.CharField(max_length=100, default=None, blank=True,
                              verbose_name="Reason for change")
    endDate = models.DateField(verbose_name="Revised Project End Date",
                               default=None, blank=False, null=False)
    revisedEffort = models.IntegerField(default=0,
                                        verbose_name="Revised Effort")
    revisedTotal = models.DecimalField(default=0.0,
                                       max_digits=12,
                                       decimal_places=2,
                                       verbose_name="Revised amount")
    closed = models.BooleanField(default=False,
                                 verbose_name="Close the Project")
    closedOn = models.DateField(default=None, blank=True, null=True)
    signed = models.BooleanField(default=False,
                                 verbose_name="Contract Signed")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.crId
