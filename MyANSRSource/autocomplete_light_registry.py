import autocomplete_light
from MyANSRSource.models import ProjectTeamMember

class MemberAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['member']
autocomplete_light.register(ProjectTeamMember, MemberAutocomplete)
