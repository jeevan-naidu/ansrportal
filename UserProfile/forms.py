from django import forms
from models import MyProfile
from dal import autocomplete

class MyProfileForm(forms.ModelForm):


	user = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	first_name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
	middle_name = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	date_of_birthO = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	date_of_birthR = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	designation = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	location = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	business_unit = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	bloodgroup = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	joined = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	personal_email = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	mobile_phone = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	land_phone = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	
	class Meta:
		model = MyProfile
		fields = '__all__'

class MyProjectsForm(forms.ModelForm):

	project = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	startDate = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))
	endDate = forms.CharField(widget=forms.TextInput(attrs={'size': '30'}))

	class Meta:
		model = MyProfile
		fields = '__all__'

