from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Database Models

BU = (
    ('E', 'Editorial'),
    ('M', 'Media'),
)
PROJECT_TYPE = (
    ('Q', 'Questions'),
    ('P', 'Powerpoint'),
    ('I', 'Instructional')
)


class Book(models.Model):
    name = models.CharField(max_length=100, null=False,
                            verbose_name="Book Name")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


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
    projectType = models.CharField(
        default='Q',
        choices=PROJECT_TYPE,
        max_length=2,
        verbose_name="Project Type"
    )
    bu = models.CharField(
        default='E',
        choices=BU,
        max_length=2,
        verbose_name="Business Unit"
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
        verbose_name="project Signed"
    )
    internal = models.BooleanField(
        blank=False,
        default=True,
        null=False,
        verbose_name="Internal Project"
    )
    projectId = models.CharField(max_length=15, null=False)
    startDate = models.DateTimeField(verbose_name="Project Start Date")
    endDate = models.DateTimeField(verbose_name="Project End Date")
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
    totalValue = models.IntegerField(default=0, verbose_name="Total Value")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class TimeSheetEntry(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project Name", null=True)
    # Week details
    wkstart = models.DateField(default=None, blank=True,
                               verbose_name="Week Start")
    wkend = models.DateField(default=None, blank=True, verbose_name="Week End")

    chapter = models.ForeignKey(Chapter, verbose_name="Chapter", null=True)
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
    totalQ = models.IntegerField(default=0, verbose_name="Total")
    totalH = models.IntegerField(default=0, verbose_name="Total")
    approved = models.BooleanField(default=False, verbose_name="Approved")

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


class Holiday(models.Model):
    # project change Request Fields
    name = models.CharField(verbose_name="Holiday Name",
                            max_length="100",
                            null=True,
                            blank=True)
    date = models.DateField(verbose_name="Holiday Date")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class ProjectChangeInfo(models.Model):
    # project change Request Fields
    project = models.ForeignKey(Project, verbose_name="Project Name")
    changedOn = models.DateField(auto_now_add=True,
                                 verbose_name="Changed On", default=None)
    crId = models.CharField(default=None, blank=True,
                            max_length=100, verbose_name="Change Request ID")
    reason = models.CharField(max_length=100, default=None, blank=True,
                              verbose_name="Reason for change")
    endDate = models.DateField(verbose_name="Revised Project End Date",
                               default=None, blank=True)
    revisedEffort = models.IntegerField(default=0,
                                        verbose_name="Revised Effort")
    closed = models.BooleanField(default=False,
                                 verbose_name="Close the Project")
    # Check lateset change or not
    status = models.BooleanField(default=False,
                                 verbose_name="Status")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class ProjectMilestone(models.Model):
    project = models.ForeignKey(Project)
    milestoneDate = models.DateField(verbose_name="Milestone Date",
                                     default=timezone.now)
    deliverables = models.CharField(default=None, blank=True, max_length=100,
                                    verbose_name="Deliverables")
    description = models.CharField(default=None, blank=True, max_length=1000,
                                   verbose_name="Description")
    amount = models.IntegerField(default=0, verbose_name="Amount")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class ProjectTeamMember(models.Model):
    project = models.ForeignKey(Project)
    member = models.ForeignKey(User)
    role = models.CharField(default=None, blank=True, max_length=100,
                            verbose_name="Role")
    startDate = models.DateField(verbose_name='Start date on project',
                                 default=timezone.now)
    endDate = models.DateField(verbose_name='End date on project',
                               default=timezone.now)
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.member)
