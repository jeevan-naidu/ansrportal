from django.shortcuts import render
import datetime
from django.utils import timezone
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib import messages
from forms import FilterGrievanceForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from Grievances.models import Grievances, Grievances_catagory, SATISFACTION_CHOICES, \
    STATUS_CHOICES, STATUS_CHOICES_CLOSED
from Grievances.views import AllowedFileTypes


class GrievanceAdminListView(ListView):
    template_name = "GrievancesAdmin_list.html"
    model = Grievances

    def get_context_data(self, **kwargs):
        context = super(GrievanceAdminListView, self).get_context_data(**kwargs)
        context['grievances'] = Grievances.objects.all().order_by("-created_date")
        context['users'] = User.objects.filter(is_active=True)
        context['category'] = Grievances_catagory.objects.filter(active=True)

        context['grievances_choices'] = STATUS_CHOICES_CLOSED
        form = FilterGrievanceForm()
        context['form'] = form

        if 'page' not in self.request.GET:
            if 'grievance' in self.request.session:
                del self.request.session['grievance']

        if 'grievance' in self.request.session:
            context['grievances'] = self.request.session['grievance']

        return context

    def post(self, request, *args, **kwargs):
        form = FilterGrievanceForm(request.POST)
        TZ = timezone.pytz.timezone(settings.TIME_ZONE)
        if 'user' not in request.POST:
            user = request.POST.get('user-autocomplete')
        else:
            user = request.POST.get('user')

        category = request.POST.get('catagory')
        status = request.POST.get('grievance_status')
        if status == 'True':
            status = True
        elif status == 'False':
            status = False
        from_date = request.POST.get('created_date')
        if from_date:
            from_date_list = from_date.split("/")
            actual_from_date = from_date_list[2] + '-' + from_date_list[1] + '-' + from_date_list[0]+' 0:00:00'
            actual_from_date = timezone.datetime.strptime(actual_from_date,'%Y-%m-%d %H:%M:%S')
            actual_from_date = timezone.make_aware(actual_from_date, TZ)
        to_date = request.POST.get('closure_date')
        if to_date:
            to_date_list = to_date.split("/")
            to_from_date = to_date_list[2] + '-' + to_date_list[1] + '-' + to_date_list[0]+' 23:59:59'
            to_from_date = timezone.datetime.strptime(to_from_date, '%Y-%m-%d %H:%M:%S')
            to_from_date = timezone.make_aware(to_from_date, TZ)
            to_from_date = to_from_date + datetime.timedelta(days=1)

        context_users = User.objects.filter(is_active=True)
        context_category = Grievances_catagory.objects.filter(active=True)
        if user != '' and category != '' and status != '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(user=user, catagory=category, grievance_status=status,
                                                   created_date__range=[actual_from_date, to_from_date])  # all chosen

        if user != '' and category == '' and status == '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(user=user)  # only user

        if user == '' and category != '' and status == '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(catagory=category)  # only category

        if user == '' and category == '' and status != '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(grievance_status=status)  # only status

        if user == '' and category == '' and status == '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(created_date__range=[actual_from_date, to_from_date])  # only dates

        if user != '' and category != '' and status == '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(user=user, catagory=category)  # user and category

        if user != '' and category == '' and status != '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(user=user, grievance_status=status)  # user and status

        if user != '' and category != '' and status != '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(user=user, catagory=category,
                                                   grievance_status=status)  # user, category and status

        if user != '' and category == '' and status == '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(user=user,
                                                   created_date__range=[actual_from_date, to_from_date])  # user, date

        if user == '' and category != '' and status != '' and from_date == '' and to_date == '':
            grievances = Grievances.objects.filter(catagory=category, grievance_status=status)  # category and status

        if user == '' and category != '' and status == '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(catagory=category,
                                                   created_date__range=[actual_from_date,
                                                                        to_from_date])  # category, date
        if user == '' and category == '' and status != '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(grievance_status=status,
                                                   created_date__range=[actual_from_date, to_from_date])  # status, date

        if user == '' and category != '' and status != '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(catagory=category, grievance_status=status,
                                                   created_date__range=[actual_from_date,
                                                                        to_from_date])  # category, status and date

        if user != '' and category == '' and status != '' and from_date != '' and to_date != '':
            grievances = Grievances.objects.filter(user=user, grievance_status=status,
                                                   created_date__range=[actual_from_date,
                                                                        to_from_date])  # user, status and date
        if grievances.count > 0:
            self.request.session['grievance'] = grievances

        if 'grievance' in self.request.session:
            grievances = self.request.session['grievance']

        return render(self.request, self.template_name, {'grievances': grievances, 'category': context_category,
                                                         'users': context_users,
                                                         'grievances_choices': STATUS_CHOICES_CLOSED, 'form': form})


def read_file_size(attachment):
    blob = attachment.read()
    return len(blob)


class GrievanceAdminEditView(TemplateView):
    template_name = "GrievancesAdmin_edit.html"

    def get_context_data(self, **kwargs):
        context = super(GrievanceAdminEditView, self).get_context_data(**kwargs)
        context['grievances'] = Grievances.objects.get(pk=self.kwargs['id'])
        if not context['grievances'].active:
            context['grievances_choices'] = STATUS_CHOICES_CLOSED
        else:
            context['grievances_choices'] = STATUS_CHOICES
        context['grievances_satisfaction_choices'] = SATISFACTION_CHOICES
        return context

    def post(self, request, **kwargs):
        grievance_id = request.POST.get('grievance_id')
        attachment_error = 0
        try:
            grievances = Grievances.objects.get(pk=grievance_id)
        except grievances.DoesNotExist:
            messages.error(self.request, "Sorry Please try Again")

        if request.POST.get('check_admin_closure_message_attachment'):
            grievances.admin_closure_message_attachment = ''
        if request.POST.get('check_admin_action_attachment'):
            grievances.admin_action_attachment = ''

        grievances.escalate_to = request.POST.get('escalate_to')
        grievances.action_taken = request.POST.get('action_taken').strip()

        if request.FILES.get('admin_action_attachment', ""):
            if request.FILES['admin_action_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                attachment_error += 1
                messages.warning(self.request, 'Attachment : File type not allowed.\
                 Please select a valid file type and then submit again')

            elif read_file_size(request.FILES['admin_action_attachment']) > settings.GRIEVANCE_ADMIN_MAX_UPLOAD_SIZE:
                attachment_error += 1
                messages.warning(self.request, 'Please upload File Size Less Than 1MB')

            else:
                grievances.admin_action_attachment = request.FILES['admin_action_attachment']

        grievances.admin_closure_message = request.POST.get('admin_closure_message').strip()

        if request.FILES.get('admin_closure_message_attachment', ""):
            if request.FILES['admin_closure_message_attachment'].name.split(".")[-1] not in AllowedFileTypes:
                attachment_error += 1
                messages.warning(self.request, 'Attachment : File type not allowed.\
                 Please select a valid file type and then submit again')

            elif read_file_size(request.FILES['admin_closure_message_attachment']) >\
                    settings.GRIEVANCE_ADMIN_MAX_UPLOAD_SIZE:
                attachment_error += 1
                messages.warning(self.request, 'Please upload File Size Less Than 1MB')

            else:
                grievances.admin_closure_message_attachment = request.FILES['admin_closure_message_attachment']

        grievances.grievance_status = request.POST.get('grievance_status')

        if attachment_error == 0:
            if grievances.id:
                database_object = Grievances.objects.get(id=grievances.id)

                if database_object.escalate_to is None:
                    database_object.escalate_to = " "  # because for next line if
                    # grievances.escalte_to is empty string from form, then we cant compare none type
                    # and empty string, so make 'None' to empty string
                if database_object.escalate_to != grievances.escalate_to:
                    EscalateToList = grievances.escalate_to.replace("'", "").replace('"', '').split(";")
                    msg_html = render_to_string('email_templates/EscalateToTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_id':database_object.grievance_id,
                                                 'grievance_subject':database_object.subject})

                    mail_obj = EmailMessage('Escalation - Grievance Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, EscalateToList,
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")

                if not database_object.action_taken and grievances.action_taken :
                    # this means the HR has taken action on the grievance.
                    # Send mails to the HR as well as the employee and update the date

                    msg_html = render_to_string('email_templates/ActionTakenTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_id': database_object.grievance_id,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Action taken - Grievance Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [database_object.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")
                    grievances.action_taken_date = datetime.datetime.now()

                elif database_object.action_taken != grievances.action_taken:
                    # this means the HR has edited/changed the action taken field.
                    # Send update mails to the HR as well as the employee and update the date
                    msg_html = render_to_string('email_templates/EditActionTakenTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Change in action taken - Grievance Id - ' +
                                            database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER,
                                            [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()
                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")

                    grievances.action_taken_date = datetime.datetime.now()

                if database_object.admin_closure_message is None:
                    database_object.admin_closure_message = " "  # because for next line if
                    # grievances.admin_closure_message is empty string coming from form, then we
                    # cant compare none type and empty string, so make 'None' to empty string

                if database_object.admin_closure_message == "" and grievances.admin_closure_message:
                    # this means the HR has added the closure message. Send mails to
                    # HR and the user and update the date.
                    msg_html = render_to_string('email_templates/AdminClosureMessageTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('HR Message - Grievance  Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [self.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()
                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")

                    grievances.admin_closure_message_date = datetime.datetime.now()

                elif database_object.admin_closure_message != grievances.admin_closure_message:
                    # this means HR has edited/changed the closure message. Send update mails
                    #  to the HR aas well as the employee and update the date field.
                    msg_html = render_to_string('email_templates/EditAdminClosureMessageTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Change in admin message - Grievance Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [database_object.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")

                    grievances.admin_closure_message_date = datetime.datetime.now()

                elif database_object.active == False and grievances.active == True:
                    # this means the HR wants to reopen this grievance. Send mails to HR and the employee
                    msg_html = render_to_string('email_templates/OpenClosedGrievanceMessageTemplate.html', {
                        'registered_by': database_object.user.first_name, 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Closed grievance opened - Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [database_object.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()
                    if email_status < 1:
                        messages.success(self.request, "Unable TO Inform Authorities")

            grievances.save()
            messages.success(self.request, "Successfully Updated")

        return HttpResponseRedirect('/grievances_admin/edit/' + grievance_id)

