from __future__ import absolute_import
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from celery.task import Task
from django.conf import settings
from celery.registry import tasks

import logging

logger = logging.getLogger('MyANSRSource')


class ExitEmailSendTask(Task):
    def run(self, user, optionallast_date,dateofresignataion,user_email, manager_email):
        msg_html = render_to_string('email_templates/employee_exit.html',
                                    {'registered_by': user.first_name,
                                    'last_date': optionallast_date,
                                     'resign_date':dateofresignataion})

        mail_obj = EmailMessage('Employee Resignation Request',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email, manager_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class PostAcceptedMailMGR(Task):
    def run(self, username, user_email, laste_date_accepted, manager_email):
        msg_html = render_to_string('email_templates/acceptence_email.html',
                                    {'registered_by': username,
                                    'last_date_accepted': laste_date_accepted, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email, manager_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class PostAcceptedMailHR(Task):
    def run(self, username, user_email, laste_date_accepted, ):
        msg_html = render_to_string('email_templates/acceptence_emailhr.html',
                                    {'registered_by': username,
                                    'last_date_accepted': laste_date_accepted, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class LibraryClearanceMail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/library_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=[])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class AdayBeforeEmail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/resingedcandidateemail.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage(username + ' Last day',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=[])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class FinanceClearanceMail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/it_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class AdminClearanceMail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/admin_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class FacilityClearanceMail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/Facility_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class MGRClearanceMail(Task):
    def run(self, username, user_email, mgr_email):
        msg_html = render_to_string('email_templates/MGR_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email,
                                                                     mgr_email],
                                cc=[''])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


class HRClearanceMail(Task):
    def run(self, username, user_email, ):
        msg_html = render_to_string('email_templates/HR_email.html',
                                    {'registered_by': username, })

        mail_obj = EmailMessage('Resignation Acceptance',
                                msg_html, settings.EMAIL_HOST_USER, ['pupul.ranjan@ansrsource.com', user_email],
                                cc=['balamurugan.rs@ansrsource.com'])

        mail_obj.content_subtype = 'html'
        email_status = mail_obj.send()
        if email_status == 0:
                    logger.error(
                        "Unable To send Mail To The Authorities For"
                        "The Following Exit Applicant : Date time : ")
                    return "failed"
        else:
            logger.debug('send successful')


tasks.register(ExitEmailSendTask)
tasks.register(PostAcceptedMailMGR)
tasks.register(PostAcceptedMailHR)
tasks.register(AdayBeforeEmail)
tasks.register(AdminClearanceMail)
tasks.register(LibraryClearanceMail)
tasks.register(FacilityClearanceMail)
tasks.register(HRClearanceMail)
tasks.register(MGRClearanceMail)
tasks.register(FacilityClearanceMail)
