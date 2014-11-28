from selectable.base import ModelLookup
from selectable.registry import registry
from django.contrib.auth.models import User

class MemberLookup(ModelLookup):
    model = User
    search_fields = ('username__icontains', )

registry.register(MemberLookup)
