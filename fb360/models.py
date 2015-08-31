from django.db import models
from django.contrib.auth.models import User

# Choice field declaration
STATUS = (
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
    ('D', 'Deleted'),
    )

CATEGORY = (
    ('P', 'Peers'),
    ('R', 'Reportees'),
    ('M', 'Manager'),
    )

# Year choice ranges from 2015 to 9999
YEAR = [(k, v) for k, v in enumerate([i for i in xrange(2015, 10000)])]


# FB360 Models
class EmpPeer(models.Model):

    """
    Information about employee and their peers
    """
    employee = models.ForeignKey(User, verbose_name="Employee",
                                 related_name="Eempl", default=None)
    peer = models.ManyToManyField(User, verbose_name="Peer(s)",
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
    year = models.IntegerField(
        verbose_name='Year',
        choices=YEAR,
        default=0
    )
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)


class Answer(models.Model):

    """
    Set of answers that a question can possibly have
    """
    ans = models.CharField("Question", max_length=100, blank=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.ans


class Question(models.Model):

    """
    QA assigned with its respective category
    """
    qst = models.CharField("Question", max_length=100, blank=False)
    ans = models.ManyToManyField(Answer,
                                 verbose_name="Feedback Question",
                                 default=None)
    category = models.CharField(
        verbose_name='Question Category',
        max_length=1,
        choices=CATEGORY,
        default=CATEGORY[0][0])
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.qst


class Feedback(models.Model):

    """
    Feedback Information
    """
    qst = models.ForeignKey(Question,
                            verbose_name="Feedback Question",
                            default=None)
    year = models.IntegerField(
        verbose_name='Year',
        choices=YEAR,
        default=0
    )
    # Feedback process planning
    start_date = models.DateTimeField(
        verbose_name="Start 360 degree appraisal"
    )
    end_date = models.DateTimeField(
        verbose_name="Complete 360 degree appraisal"
    )
    # Peer dates
    selection_date = models.DateTimeField(
        verbose_name="Peer selection completion date"
    )
    approval_date = models.DateTimeField(
        verbose_name="Peer approval completion date"
    )
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
    ans = models.ForeignKey(Answer,
                            default=None)
    year = models.IntegerField(default=0)
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
