from django.db import models
from django.contrib.auth.models import User
import employee as emp
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.db import IntegrityError

# Choice field declaration
STATUS = (
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
    ('D', 'Deleted'),
    )

QST_TYPE = (
    ('Q', 'Qualitative'),
    ('M', 'Multiple Choice'),
    )

RESPONDENT_TYPES = (
    ('P', "Peer"),
    ('E', "Reportee"),
    ('M', "Manager"),
)

# Year choice ranges from 2015 to 3999
YEAR = [(v, v) for k, v in enumerate([i for i in xrange(2015, 4000)])]


class FB360(models.Model):

    """
    Feedback Information
    """
    name = models.CharField("Name", max_length=100, blank=False, default=None)
    eligible = models.ManyToManyField(
        User,
        verbose_name='Eligible Person(s)',
        default=None)
    # Feedback process planning
    start_date = models.DateField(
        verbose_name="Start 360 degree appraisal"
    )
    end_date = models.DateField(
        verbose_name="Complete 360 degree appraisal"
    )
    # Peer / Reportee dates
    # Reportee and Peer have same dates
    selection_date = models.DateField(
        verbose_name="Peer / Reportee selection completion date"
    )
    approval_date = models.DateField(
        verbose_name="Peer / Reportee approval completion date"
    )
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return str(self.name)

    class Meta:
        verbose_name = 'FB360 Information'
        verbose_name_plural = 'FB360 Information'


# This tweek is to add manager -> reportee relationship.
# As default, manager has to give
# feedback to thier reportee.
def DefaultRelation(sender, instance, **kwargs):
    """
    Helper to insert default realtion (manager -> Reportee)
    for selected su rvey
    Returns Nothing
    """
    eligible = FB360.objects.filter(id=instance.id).values('eligible')
    fbObj = FB360.objects.get(id=instance.id)
    for eachEligible in eligible:
        # Check to confirm if eligible is none or not
        if eachEligible['eligible'] is not None:
            cUser = User.objects.get(id=eachEligible['eligible'])
            # Escapes user who doesn't have a manager
            try:
                initObj = Initiator()
                initObj.survey = fbObj
                initObj.employee = cUser
                initObj.save()
            except IntegrityError:
                initObj = Initiator.objects.get(survey=fbObj, employee=cUser)
            if cUser.employee.manager is not None:
                respObj = Respondent()
                respObj.employee = cUser.employee.manager.user
                respObj.initiator = initObj
                respObj.status = STATUS[1][0]
                respObj.respondent_type = RESPONDENT_TYPES[2][0]
                respObj.save()

post_save.connect(DefaultRelation,
                  sender=FB360,
                  dispatch_uid="Add Default Relation")


# FB360 Models
class Initiator(models.Model):

    """
    Information about employee and their feedback respondent
    """
    survey = models.ForeignKey(FB360, default=None)
    employee = models.ForeignKey(User, related_name="emp",
                                 default=None)
    respondents = models.ManyToManyField(User,
                                         verbose_name="Choose Respondent",
                                         through='Respondent',
                                         related_name="Epeer", default=None)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    class Meta:
        unique_together = ('employee', 'survey', )


class Respondent(models.Model):

    """
    Intermediate table for respondents
    """
    employee = models.ForeignKey(User, verbose_name="Respondent",
                                 related_name="Pempl", default=None)
    initiator = models.ForeignKey(Initiator,
                                  verbose_name="Initiator",
                                  related_name="Pempl", default=None)
    respondent_type = models.CharField(
        verbose_name='Respondent Type',
        max_length=1,
        choices=RESPONDENT_TYPES,
        default=RESPONDENT_TYPES[0][0])
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
        unique_together = ('employee', 'initiator', 'respondent_type', )


class Group(models.Model):

    """
    Group to manage question
    """
    name = models.CharField("Name", max_length=100, blank=False)
    priority = models.IntegerField("Priority", max_length=100,
                                   validators=[MinValueValidator(0)],
                                   blank=False)
    fb = models.ForeignKey(FB360, default=None)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.name


class Question(models.Model):

    """
    QA assigned with its respective category
    """
    qst = models.CharField("Question", max_length=256, blank=False)
    priority = models.IntegerField("Priority", max_length=100,
                                   validators=[MinValueValidator(0)],
                                   blank=False, default=None)
    qtype = models.CharField(
        verbose_name='Type',
        max_length=1,
        choices=QST_TYPE,
        default=QST_TYPE[0][0])
    group = models.ForeignKey(Group, default=None)
    category = models.ManyToManyField(
        emp.models.Designation,
        default=None,
        verbose_name="Roles")
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)

    def __unicode__(self):
        return self.qst

    class Meta:
        ordering = ('category__name', )


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
    submitted = models.BooleanField(default=False)
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
    qst = models.ForeignKey(Question,
                            default=None)
    general_fb = models.CharField("Feedback", max_length=500, blank=False)
    year = models.IntegerField(default=0)
    submitted = models.BooleanField(default=False)
    createdon = models.DateTimeField(verbose_name="created Date",
                                     auto_now_add=True)
    updatedon = models.DateTimeField(verbose_name="Updated Date",
                                     auto_now=True)
