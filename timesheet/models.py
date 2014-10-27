from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from smart_selects.db_fields import ChainedForeignKey
# Database Models

TASK = (
    ('D', 'Develop'),
    ('R', 'Review'),
    ('C', 'Copy Edit'),
    ('Q', 'QA'),
    ('I', 'Idle'),
)


class Book(models.Model):
    name = models.CharField(max_length=100, verbose_name="Book Name")
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
    name = models.CharField(max_length=50, verbose_name="Project Name")
    startDate = models.DateTimeField(verbose_name="Project Start Date",
                                     default=timezone.now)
    endDate = models.DateTimeField(verbose_name="Project End Date",
                                   default=timezone.now)
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort")
    contingencyEffort = models.IntegerField(default=0,
                                            verbose_name="Contigency Effort")
    projectManager = models.ForeignKey(User)
    # Chapters to be worked on in the project
    chapters = models.ManyToManyField(Chapter)
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.name)


class Activity(models.Model):
    name = models.CharField(max_length=50, verbose_name="Activity Name")
    wkstart = models.DateField(default=None, blank=True,
                               verbose_name="Week Start")
    wkend = models.DateField(default=None, blank=True,
                             verbose_name="Week End")
    monday = models.IntegerField(default=0,
                                 verbose_name="Monday")
    tuesday = models.IntegerField(default=0,
                                  verbose_name="Tuesday")
    wednesday = models.IntegerField(default=0,
                                    verbose_name="Wednesday")
    thursday = models.IntegerField(default=0,
                                   verbose_name="Thursday")
    friday = models.IntegerField(default=0,
                                 verbose_name="Friday")
    saturday = models.IntegerField(default=0,
                                   verbose_name="Saturday")
    total = models.IntegerField(default=0,
                                verbose_name="Total", )
    managerFeedback = models.CharField(default=None, blank=True,
                                       max_length=1000,
                                       verbose_name="Manager Feedback")
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class TimeSheetEntry(models.Model):
    project = models.ForeignKey(Project, verbose_name="Project Name")
    # Week details
    wkstart = models.DateField(default=None, blank=True,
                               verbose_name="Week Start")
    wkend = models.DateField(default=None, blank=True,
                             verbose_name="Week End")

    chapter = ChainedForeignKey(
        Chapter,
        chained_field="project",
        chained_model_field="project",
        show_all=False,
        auto_choose=True,
        verbose_name="Chapter"
    )
    task = models.CharField(choices=TASK, default='D',
                            verbose_name='Task', max_length=2)
    # Effort capture
    monday = models.IntegerField(default=0,
                                 verbose_name="Mon")
    tuesday = models.IntegerField(default=0,
                                  verbose_name="Tue")
    wednesday = models.IntegerField(default=0,
                                    verbose_name="Wed")
    thursday = models.IntegerField(default=0,
                                   verbose_name="Thu")
    friday = models.IntegerField(default=0,
                                 verbose_name="Fri")
    saturday = models.IntegerField(default=0,
                                   verbose_name="Sat")
    questionsCreated = models.IntegerField(default=0,
                                           verbose_name="Question Created"
                                           )
    total = models.IntegerField(default=0,
                                verbose_name="Total")
    approved = models.BooleanField(default=False,
                                   verbose_name="Approved")

    # Approval related details
    approvedon = models.DateTimeField(default=None, null=True, blank=True,
                                      verbose_name="Approved On",
                                      editable=False)
    managerFeedback = models.CharField(default=None, null=True, blank=True,
                                       max_length=1000,
                                       verbose_name="Manager Feedback")
    teamMember = models.ForeignKey(User,
                                   verbose_name="Team Members",
                                   editable=False
                                   )
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    class Meta:
        verbose_name = 'Timesheet Entry'
        verbose_name_plural = 'Timesheet Entries'


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
    plannedEffort = models.IntegerField(default=0,
                                        verbose_name="Planned Effort")
    # Record Entered / Updated Date
    createdOn = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedOn = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return unicode(self.member)
