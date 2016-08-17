from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
from django.core.validators import validate_email
from django.template.loader import render_to_string
from Grievances.models import Grievances, Grievances_category, SATISFACTION_CHOICES, \
    STATUS_CHOICES, STATUS_CHOICES_CLOSED
from Grievances.views import AllowedFileTypes
import logging
logger = logging.getLogger('MyANSRSource')


class GrievanceAdminListView(ListView):
    template_name = "GrievancesAdmin_list.html"
    model = Grievances

    def get_context_data(self, **kwargs):
        context = super(GrievanceAdminListView, self).get_context_data(**kwargs)
        context['grievances'] = grievances_list = Grievances.objects.all().order_by("-created_date")
        context['users'] = User.objects.filter(is_active=True)
        context['category'] = Grievances_category.objects.filter(active=True)
        context['grievances_choices'] = STATUS_CHOICES_CLOSED
        form = FilterGrievanceForm()
        context['form'] = form
	paginator = Paginator(grievances_list, 5) # Show 5 grievances per page

    	page = self.request.GET.get('page')
    	try:
            grievances_page = paginator.page(page)
    	except PageNotAnInteger:
        # If page is not an integer, deliver first page.
            grievances_page = paginator.page(1)
    	except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
            grievances_page = paginator.page(paginator.num_pages)

    	context['grievances_page'] = grievances_page
        """if 'page' not in self.request.GET:
            if 'grievance' in self.request.session:
                del self.request.session['grievance']

        if 'grievance' in self.request.session:
            context['grievances'] = self.request.session['grievance'] """

        return context

    def post(self, request, *args, **kwargs):
        form = FilterGrievanceForm(request.POST)
        grievances = []
        TZ = timezone.pytz.timezone(settings.TIME_ZONE)
        if 'user' not in request.POST:
            user = request.POST.get('user-autocomplete')
        else:
            user = request.POST.get('user')

        if 'grievance_id' not in request.POST:
            grievance_id = request.POST.get('grievance_id-autocomplete')
        else:
            grievance_id = request.POST.get('grievance_id')

        category = request.POST.get('category')
        status = request.POST.get('grievance_status')

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
        context_category = Grievances_category.objects.filter(active=True)
        try:
            if user != '' and category != '' and status != '' and from_date != '' \
                    and to_date != '' and grievance_id != '':
                grievances = Grievances.objects.filter(user=user, grievance_id=grievance_id,
                                                       category=category, grievance_status=status,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # all chosen

            if user != '' and category == '' and status == '' and from_date == '' \
                    and to_date == '' and grievance_id == '':
                grievances = Grievances.objects.filter(user=user)  # only user

            if user == '' and category != '' and status == '' and from_date == ''\
                    and to_date == '' and grievance_id == '':
                grievances = Grievances.objects.filter(category=category)  # only category

            if user == '' and category == '' and status != '' and from_date == '' \
                    and to_date == ''and grievance_id == '':
                grievances = Grievances.objects.filter(grievance_status=status)  # only status

            if user == '' and category == '' and status == '' and from_date != ''\
                    and to_date != ''and grievance_id == '':
                grievances = Grievances.objects.filter(created_date__range=[actual_from_date,
                                                                            to_from_date])  # only dates

            if user == '' and category == '' and status == '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(pk=grievance_id)  # only grievance_id

            if user != '' and category != '' and status == '' and from_date == ''\
                    and to_date == ''and grievance_id == '':
                grievances = Grievances.objects.filter(user=user, category=category)  # user and category
            # import pdb;pdb.set_trace();
            if user != '' and category == '' and status != '' and from_date == '' \
                    and to_date == ''and grievance_id == '':
                grievances = Grievances.objects.filter(user=user, grievance_status=status)  # user and status

            if user != '' and category == '' and status == '' and \
                            from_date == '' and to_date == ''and grievance_id != '':
                grievances = Grievances.objects.filter(user=user, pk=grievance_id)  # user and grievance_id

            if user != '' and category != '' and status != '' and from_date == '' \
                    and to_date == ''and grievance_id == '':
                grievances = Grievances.objects.filter(user=user, category=category,
                                                       grievance_status=status)  # user, category and status

            if user != '' and category != '' and status == '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(user=user, grievance_status=status,
                                                       pk=grievance_id)  # user, status and grievance_id

            if user == '' and category != '' and status != '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(pk=grievance_id, category=category,
                                                       grievance_status=status)  # grievance_id, category and status

            if user != '' and category == '' and status != '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(user=user, category=category,
                                                       pk=grievance_id)  # user, category and grievance_id

            if user != '' and category == '' and status == '' and from_date != '' \
                    and to_date != ''and grievance_id == '':
                grievances = Grievances.objects.filter(user=user,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # user, date

            if user != '' and category == '' and status == '' and from_date != ''and to_date != ''  \
                    and grievance_id != '':
                grievances = Grievances.objects.filter(user=user,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date],
                                                       pk=grievance_id)  # user, date and grievance_id

            if user == '' and category != '' and status != '' and from_date == '' \
                    and to_date == ''and grievance_id == '':
                grievances = Grievances.objects.filter(category=category,
                                                       grievance_status=status)  # category and status

            if user == '' and category != '' and status == '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(category=category,
                                                       pk=grievance_id)  # category and grievance_id

            if user == '' and category != '' and status != '' and from_date == '' \
                    and to_date == '' and grievance_id != '':
                grievances = Grievances.objects.filter(grievance_status=status,
                                                       pk=grievance_id)  # status, grievance_id
            if user == '' and category != '' and status != '' and from_date != '' \
                    and to_date != '' and grievance_id != '':
                grievances = Grievances.objects.filter(grievance_status=status,
                                                       pk=grievance_id,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date],)  # status, grievance_id,date

            if user == '' and category != '' and status == '' and from_date != '' \
                    and to_date != '' and grievance_id == '':
                grievances = Grievances.objects.filter(category=category,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # category, date

            if user == '' and category != '' and status == '' and from_date != '' \
                    and to_date != '' and grievance_id != '':
                grievances = Grievances.objects.filter(category=category,  pk=grievance_id,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # category,date,grievance_id

            if user == '' and category == '' and status == '' and from_date != '' \
                    and to_date != ''and grievance_id != '':
                grievances = Grievances.objects.filter(pk=grievance_id,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # grievance_id, date

            if user == '' and category == '' and status != '' and from_date != ''\
                    and to_date != '' and grievance_id == '':
                grievances = Grievances.objects.filter(grievance_status=status,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # status, date

            if user == '' and category != '' and status != '' and from_date != '' \
                    and to_date != '' and grievance_id == '':
                grievances = Grievances.objects.filter(category=category, grievance_status=status,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # category, status and date

            if user != '' and category == '' and status != '' and from_date != '' \
                    and to_date != ''and grievance_id == '':
                grievances = Grievances.objects.filter(user=user, grievance_status=status,
                                                       created_date__range=[actual_from_date,
                                                                            to_from_date])  # user, status and date
        except ValueError:
            grievances = None

        if grievances and grievances.count > 0:
            self.request.session['grievance'] = grievances

        if not grievances and 'grievance' in self.request.session:
            del self.request.session['grievance']

        if 'grievance' in self.request.session:
            grievances = self.request.session['grievance']

        return render(self.request, self.template_name, {'grievances': grievances, 'category': context_category,
                                                         'users': context_users,
                                                         'grievances_choices': STATUS_CHOICES_CLOSED,
                                                         'form': FilterGrievanceForm()})


def read_file_size(attachment):
    blob = attachment.read()
    return len(blob)


def validate_escalation_email(a):
    for e in a[:]:
        try:
            validate_email(e)
        except:
            a.remove(e)
    a = ','.join(a)
    return a


def remove_common_elements(a, b):
    for e in a[:]:
        try:
            validate_email(e)
        except:
            a.remove(e)
        if e.strip() in b:
            a.remove(e)

    a = ','.join(a)
    return a


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

        if not context['grievances'].escalate_to is None and ';' in context['grievances'].escalate_to:
            context['grievances'].escalate_to = context['grievances'].escalate_to.replace(';', ',')

        return context

    def post(self, request, **kwargs):
        grievance_id = self.kwargs['id']
        attachment_error = 0
        try:
            grievances = Grievances.objects.get(pk=grievance_id)
        except grievances.DoesNotExist:
            messages.error(self.request, "Sorry Please try Again")

        if request.POST.get('check_admin_closure_message_attachment'):
            grievances.admin_closure_message_attachment = ''
        if request.POST.get('check_admin_action_attachment'):
            grievances.admin_action_attachment = ''
        grievances.escalate_to = (request.POST.get('escalate_to'))
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

        grievances.grievance_status = request.POST.get('grievance_status').strip()

        if attachment_error == 0:
            email_status = None
            if grievances.id:
                database_object = Grievances.objects.get(id=grievances.id)

                if database_object.action_taken:
                    database_object.action_taken = database_object.action_taken.strip()
                if grievances.action_taken:
                    grievances.action_taken = grievances.action_taken.strip()
                if database_object.admin_closure_message:
                    database_object.admin_closure_message = database_object.admin_closure_message.strip()
                if grievances.admin_closure_message:
                    grievances.admin_closure_message = grievances.admin_closure_message.strip()

                if database_object.escalate_to is None:
                    database_object.escalate_to = " "  # because for next line if
                    # grievances.escalte_to is empty string from form, then we cant compare none type
                    # and empty string, so make 'None' to empty string
                if database_object.escalate_to != grievances.escalate_to and grievances.escalate_to is not None:
                    EscalatetoList = remove_common_elements((grievances.escalate_to.split(',')),
                                                            (database_object.escalate_to.split(',')))

                    EscalatetoList = EscalatetoList.replace("'", "").replace('"', '').split(",")
                    EscalatetoList = list(filter(None, EscalatetoList))
                    grievances.escalate_to = validate_escalation_email(request.POST.get('escalate_to').split(','))
                    if not EscalatetoList:  # empty EscalatetoList list
                        pass
                    else:
                        msg_html = render_to_string('email_templates/EscalateToTemplate.html',
                                                    {'registered_by': database_object.user.first_name,
                                                     'grievance_id': database_object.grievance_id,
                                                     'grievance_subject': database_object.subject})

                        mail_obj = EmailMessage('Escalation - Grievance Id - ' + database_object.grievance_id,
                                                msg_html, settings.EMAIL_HOST_USER, EscalatetoList,
                                                cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                        mail_obj.content_subtype = 'html'
                        email_status = mail_obj.send()

                if not database_object.action_taken and grievances.action_taken and grievances.action_taken is not None:
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

                    grievances.action_taken_date = timezone.make_aware(datetime.datetime.now(),
                                                                       timezone.get_default_timezone())

                elif database_object.action_taken != grievances.action_taken and grievances.action_taken is not None:
                    # this means the HR has edited/changed the action taken field.
                    # Send update mails to the HR as well as the employee and update the date
                    msg_html = render_to_string('email_templates/EditActionTakenTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_id': database_object.grievance_id,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Change in action taken - Grievance Id - ' +
                                            database_object.grievance_id, msg_html, settings.EMAIL_HOST_USER,
                                            [database_object.user.email], cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                    grievances.action_taken_date = timezone.make_aware(datetime.datetime.now(),
                                                                       timezone.get_default_timezone())

                if database_object.admin_closure_message is None:
                    database_object.admin_closure_message = " "  # because for next line if
                    # grievances.admin_closure_message is empty string coming from form, then we
                    # cant compare none type and empty string, so make 'None' to empty string

                if database_object.admin_closure_message == "" and grievances.admin_closure_message \
                        and grievances.admin_closure_message is not None:
                    # this means the HR has added the closure message. Send mails to
                    # HR and the user and update the date.
                    msg_html = render_to_string('email_templates/AdminClosureMessageTemplate.html',
                                                {'registered_by': database_object.user.first_name,
                                                 'grievance_id': database_object.grievance_id,
                                                 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('HR Message - Grievance  Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [self.request.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                    grievances.admin_closure_message_date = timezone.make_aware(datetime.datetime.now(),
                                                                                timezone.get_default_timezone())

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

                    grievances.admin_closure_message_date = timezone.make_aware(datetime.datetime.now(),
                                                                                timezone.get_default_timezone())

                elif database_object.active == False and grievances.active == True:
                    # this means the HR wants to reopen this grievance. Send mails to HR and the employee
                    msg_html = render_to_string('email_templates/OpenClosedGrievanceMessageTemplate.html', {
                        'registered_by': database_object.user.first_name, 'grievance_subject': database_object.subject})

                    mail_obj = EmailMessage('Closed grievance opened - Id - ' + database_object.grievance_id,
                                            msg_html, settings.EMAIL_HOST_USER, [database_object.user.email],
                                            cc=[settings.GRIEVANCES_ADMIN_EMAIL])

                    mail_obj.content_subtype = 'html'
                    email_status = mail_obj.send()

                if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        " The Following Grievance: {0} Date time : {1} ".format(
                            grievances.grievance_id, timezone.make_aware(datetime.datetime.now(),
                                                                         timezone.get_default_timezone())))

            grievances.save()
            messages.success(self.request, "Successfully Updated")

        return HttpResponseRedirect('/grievances_admin/edit/' + grievance_id)

