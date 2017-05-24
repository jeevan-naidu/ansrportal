from django import forms
from datetime import datetime


class EmployeeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


class DesignationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + " | " + obj.role.name


class SetCurrentUserFormset(forms.models.BaseInlineFormSet):
    """
    This assume you're setting the 'request' and 'created_by, updated_by' properties
    before using this formset.
    """
    def save_new(self, form, commit=True):
        """
        This is called when a new instance is being created.
        """
        obj = super(SetCurrentUserFormset, self).save_new(form, commit=False)
        setattr(obj, self.created_by, self.request.user)
        if commit:
            obj.created_on = datetime.now()
            obj.save()
        return obj

    def save_existing(self, form, instance, commit=True):
        """
        This is called when updating an instance.
        """
        obj = super(SetCurrentUserFormset, self).save_existing(form, instance, commit=False)
        setattr(obj, self.updated_by, self.request.user)
        if commit:
            obj.updated_on = datetime.now()
            obj.save()
        return obj
