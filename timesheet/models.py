from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.views import logout
# Database Models


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
    projectManager = models.ForeignKey(User, verbose_name="Project Manager",
                                       default=None, blank=True)
    # Record Entered / Updated Date
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
    # Effort capture
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
    sunday = models.IntegerField(default=0,
                                 verbose_name="Sunday")
    questionsCreated = models.IntegerField(default=0,
                                           verbose_name="Question Created"
                                           )
    approved = models.BooleanField(default=False,
                                   verbose_name="Approved")

    # Approval related details
    approvedon = models.DateTimeField(default=None, blank=True,
                                      verbose_name="Approved On",
                                      editable=False)
    managerFeedback = models.CharField(default=None, blank=True,
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
    project = models.ForeignKey(Project, verbose_name="Project Name")
    milestoneDate = models.DateField(verbose_name="Milestone Date",
                                     default=timezone.now, )
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
    project = models.ForeignKey(Project, verbose_name="Project Name")
    member = models.ForeignKey(User, verbose_name="Team Member")
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
        return self.member
