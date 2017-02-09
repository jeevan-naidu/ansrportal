from django import forms


class EmployeeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.user.first_name + " " + obj.user.last_name


class DesignationChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name + " | " + obj.role.name
