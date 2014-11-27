import autocomplete_light
from MyANSRSource.models import ProjectTeamMember


class TeamMemberAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['member']
    model = ProjectTeamMember

autocomplete_light.register(ProjectTeamMember, TeamMemberAutocomplete)
