from django.db import models
from django.contrib.auth.models import User
import employee as emp

# Choice field declaration
STATUS = (
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
    ('D', 'Deleted'),
    )

# Year choice ranges from 2015 to 3999
YEAR = [(v, v) for k, v in enumerate([i for i in xrange(2015, 4000)])]


# FB360 Models
class EmpPeer(models.Model):

    """
    Information about employee and their peers
    """
    employee = models.ForeignKey(User, related_name="emp",
                                 default=None, unique=True)
    peer = models.ManyToManyField(User, verbose_name="Choose Peer",
                                  through='Peer',
                                  related_name="Epeer", default=None)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class Peer(models.Model):

    """
    Intermediate table for Peer
    """
    employee = models.ForeignKey(User, verbose_name="Employee",
                                 related_name="Pempl", default=None)
    emppeer = models.ForeignKey(EmpPeer, verbose_name="Employee",
                                related_name="Pempl", default=None)
    status = models.CharField(
        verbose_name='Status',
        max_length=1,
        choices=STATUS,
        default=STATUS[0][0])
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    class Meta:
        unique_together = ('employee', 'emppeer', )


class FB360(models.Model):

    """
    Feedback Information
    """
    year = models.IntegerField(
        verbose_name='Year',
        choices=YEAR,
        default=0
    )
    process_start_date = models.DateField(
        default=None,
        verbose_name="Process Start Date"
    )
    # Feedback process planning
    start_date = models.DateField(
        verbose_name="Start 360 degree appraisal"
    )
    end_date = models.DateField(
        verbose_name="Complete 360 degree appraisal"
    )
    # Peer / Reportee dates
    # Reportee and Peer have same dates
    selection_start_date = models.DateField(
        default=None,
        verbose_name="Peer selection start date"
    )
    selection_date = models.DateField(
        verbose_name="Peer selection completion date"
    )
    approval_date = models.DateField(
        verbose_name="Peer approval completion date"
    )
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return str(self.year)

    class Meta:
        verbose_name = 'FB360 Information'
        verbose_name_plural = 'FB360 Informations'


class Question(models.Model):

    """
    QA assigned with its respective category
    """
    qst = models.CharField("Question", max_length=100, blank=False)
    fb = models.ForeignKey(FB360, default=None,
                           verbose_name="FB360 Information")
    category = models.ManyToManyField(
        emp.models.Designation,
        default=None)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.qst


class ManagerRequest(models.Model):

    """
    Stores manager's request and response.
    """
    respondent = models.ForeignKey(User,
                                   unique=True,
                                   related_name="Rrespon", default=None)
    status = models.CharField(max_length=1)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class Response(models.Model):

    """
    Stores FB information
    """
    employee = models.ForeignKey(User,
                                 related_name="Rempl", default=None)
    respondent = models.ForeignKey(User,
                                   related_name="Rresp", default=None)
    qst = models.ForeignKey(Question,
                            default=None)
    ans = models.CharField(max_length=8)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class QualitativeResponse(models.Model):

    """
    Stores general FB information
    """
    employee = models.ForeignKey(User, verbose_name="Employee",
                                 related_name="empl", default=None)
    respondent = models.ForeignKey(User, verbose_name="Respondent",
                                   related_name="resp", default=None)
    general_fb = models.CharField("Feedback", max_length=500, blank=False)
    year = models.IntegerField(default=0)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
