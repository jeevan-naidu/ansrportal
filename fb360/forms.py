import autocomplete_light
autocomplete_light.autodiscover()
from .models import EmpPeer

CHOICE_OPTIONS = (
    ('SA', 'Strongly agree'),
    ('A', 'Agree'),
    ('NAND', 'Neither agree nor disagree'),
    ('D', 'Disagree'),
    ('CD', 'Completely disagree'),
    )


class PeerForm(autocomplete_light.ModelForm):

    class Meta:
        model = EmpPeer
        fields = ('peer',)

    def __init__(self, *args, **kwargs):
        super(PeerForm, self).__init__(*args, **kwargs)
        self.fields['peer'].widget.attrs['class'] = "form-control"
