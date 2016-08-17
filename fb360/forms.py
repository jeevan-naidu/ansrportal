# Third-Party Plugin imports
#import autocomplete_light
#autocomplete_light.autodiscover()
from dal import autocomplete
# Our App model imports
from .models import Initiator, Respondent, Question, FB360
import employee

# Built-in imports
from django import forms

# Miscellaneous imports
from datetime import date


class SurveyForm(forms.ModelForm):

    """
        List of all surveys of current year
        whose start date is greater than or equal to today and
        end date is less than or equal to today
    """

    class Meta:
        model = Initiator
        fields = ('survey',)

        widgets = {
            'survey': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super(SurveyForm, self).__init__(*args, **kwargs)
        self.fields['survey'].widget.attrs['class'] = "form-control"
        self.fields['survey'].queryset = FB360.objects.filter(
            start_date__year=date.today().year,
            start_date__gte=date.today(),
            end_date__lte=date.today()
        ).order_by('end_date')
        self.fields['survey'].empty_label = None


# Choose Peer screen form
class PeerForm(forms.ModelForm):

    """
        Form show peer autocomplete to choose peer
        based on certain logics
    """
    class Meta:
        model = Initiator
        fields = ('respondents',)

    def __init__(self, *args, **kwargs):
        super(PeerForm, self).__init__(*args, **kwargs)
        self.fields['respondents'].widget.attrs['class'] = "form-control"


# Choose Peer screen form
class AdditionalManagerForm(forms.ModelForm):

    """
        Form show additional manager autocomplete to choose manager
        based on certain logics
    """
    class Meta:
        model = Initiator
        fields = ('respondents',)

    def __init__(self, *args, **kwargs):
        super(AdditionalManagerForm, self).__init__(*args, **kwargs)
        self.fields['respondents'].widget.attrs['class'] = "form-control"


# Choose reportee screen form
class ChooseReporteeForm(forms.ModelForm):

    """
        Form shows all my repotees
    """
    class Meta:
        model = employee.models.Employee
        fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(ChooseReporteeForm, self).__init__(*args, **kwargs)
        self.fields['user'].widget.attrs['class'] = "form-control"
        self.fields['user'].required = False


# Decide action on request screen form
class DecideOnRequestForm(forms.ModelForm):

    """
        Shows all my requests
    """
    class Meta:
        model = Respondent
        fields = ('respondent_type', 'status')

    def __init__(self, *args, **kwargs):
        super(DecideOnRequestForm, self).__init__(*args, **kwargs)
        self.fields['respondent_type'].required = False
        self.fields['status'].required = False


# Decide action on request screen form
class FB360RequesteeForm(forms.ModelForm):

    """
        Shows all my requestee list who have requested
        my feedback for them
    """
    class Meta:
        model = Respondent
        fields = ('respondent_type', )

    def __init__(self, *args, **kwargs):
        super(FB360RequesteeForm, self).__init__(*args, **kwargs)
        self.fields['respondent_type'].required = False


# Show Feedback Question
class QuestionForm(forms.ModelForm):

    """
        Shows all feedback questions
    """
    class Meta:
        model = Question
        fields = ('qst', 'priority', 'qtype', )

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)
        self.fields['qst'].required = False
        self.fields['priority'].required = False
        self.fields['qtype'].required = False
