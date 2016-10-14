from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import View
from employee.models import Employee, Designation
from CompanyMaster.models import OfficeLocation
from MyANSRSource.models import *
from models import MyProfile
from django.template import RequestContext
from forms import MyProfileForm, MyProjectsForm
# Create your views here.

class MyProfileView(View):

	def get(self, request):
		# import ipdb
		# ipdb.set_trace()
		
		# form = MyProfileForm


		# user = request.user
		# employee = Employee.objects.get(user=user)
		# teammember = ProjectTeamMember.objects.get(member=user.id)

		# first_name = user.first_name
		# last_name = user.last_name
		# middle_name = employee.middle_name
		# date_of_birthO = employee.date_of_birthO
		# date_of_birthR = employee.date_of_birthR
		# location = employee.location
		# designation = employee.designation
		# business_unit = employee.business_unit
		# bloodgroup = employee.blood_group
		# joined = employee.joined
		# mobile_phone = employee.mobile_phone
		# land_phone = employee.land_phone
		# personal_email = employee.personal_email
		# project = teammember.project
		# startDate = teammember.startDate
		# endDate = teammember.endDate

		# if request.method == 'GET':
		# 	form = MyProfileForm(request.GET)
		# 	if form.is_valid():
		# 		form.save()


		# context = {
		#'user':user,
		#'firstname':first_name, 
		#'lastname':last_name, 
		#'middlename':middle_name,
		#'date_of_birthO':date_of_birthO, 
		#'date_of_birthR':date_of_birthR,
		#'joined':joined,
		#'location':location,
		#'business_unit':business_unit,
		#'blood_group':bloodgroup,
		#'officelocation':location, 
		#'designation':designation,
		#'mobilephone': mobile_phone, 
		#'landphone':land_phone,
		#'email':personal_email, 
		#'project':project, 
		#'startDate':startDate,
		#'endDate':endDate
		#
		# 'form':form}

		


		



		#context = {'form':form}
	

		# return render(request,'myprofile.html',context)

		if request.method == 'GET':
			form = MyProfileForm(request.GET)

			if form.is_valid():
				form = Context(
					user = request.user,
					employee = Employee.objects.get(user=user),
					teammember = ProjectTeamMember.objects.get(member=user.id),
					)
				form.save()
			return render(request,'myprofile.html',{'form':form}, context_instance=RequestContext(request))