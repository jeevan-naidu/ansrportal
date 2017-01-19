from django.contrib.auth.models import User
from Leave.models import CreditEntry, LeaveSummary, LeaveType, LeaveApplications
from employee.models import Employee
from datetime import date, timedelta
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger('MyANSRSource')


class Command(BaseCommand):
    help = 'Upload Leave summary for new joinee.'

    def handle(self, *args, **options):
        new_year_migration_cron()


def new_year_migration_cron():
    users = User.objects.filter(is_active=True)

    for user in users:
        try:
            add_leave(user)
        except:
            logger.error("error happens for {0}".format(user.id))


def add_leave(user):
    leave_types = LeaveType.objects.all()
    for leave in leave_types:
        if leave.id in [1, 2, 3, 13]:
            monthly_leave_type_addition(user, leave)
        elif leave.id in [5, 6, 7, 12]:
            yearly_leave_type_addition(user, leave)
        elif leave.id in [4, 8, 9, 10, 11, 14, 15]:
            regular_leave_type_addition(user, leave)


def monthly_leave_type_addition(user, leave):
    admin = User.objects.get(id=35)
    current_month = date.today().month
    current_year = date.today().year
    if leave.id == 1:
        applied_leave_balance = float(0.0)
        applied_leave_applied = float(0.0)
        applied_leave_approved = float(0.0)
        try:
            earned_leave = LeaveSummary.objects.get(user=user,
                                                    leave_type=leave,
                                                    year=date.today().year-1)
            earned_leave = float(earned_leave.balance)
        except:
            earned_leave = float(0.0)
        # leave_applied_current_year = LeaveApplications.objects.filter(user=user,
        #                                                               leave_type=leave,
        #                                                               from_date__gte=date(day=1,
        #                                                                                   month=1,
        #                                                                                   year=date.today().year))
        # for applied_leave in leave_applied_current_year:
        #     applied_leave_balance += float(applied_leave.days_count)
        #     if applied_leave.status == 'open':
        #         applied_leave_applied += float(applied_leave.days_count)
        #     elif applied_leave.status == 'approved':
        #         applied_leave_approved += float(applied_leave.days_count)
        # if earned_leave + applied_leave_balance > 45:
        #     adjustment = (earned_leave + applied_leave_balance) - 45
        #     adjustment *= -1
        #     earned_leave += float(adjustment)
        #     CreditEntry.objects.create(user=user,
        #                                year=current_year,
        #                                month=current_month,
        #                                leave_type=leave,
        #                                days=adjustment,
        #                                status_action_by=admin,
        #                                comments="Year end adjustment by system")
        record, created = LeaveSummary.objects.get_or_create(user=user,
                                                             year=current_year,
                                                             leave_type=leave
                                                             )
        if record:
            CreditEntry.objects.create(user=user,
                                       year=current_year,
                                       month=current_month,
                                       leave_type=leave,
                                       days=leave.count,
                                       status_action_by=admin,
                                       comments="monthly leave credit given by admin")
            record.balance = float(earned_leave) + float(leave.count)
            if created:
                record.applied = 0
                record.approved = 0
            elif float(record.applied) < 0.0:
                record.applied = 0

            record.save()
    else:
        leave_entry, created = LeaveSummary.objects.get_or_create(user=user,
                                                                  year=current_year,
                                                                  leave_type=leave)
        if leave_entry:
            CreditEntry.objects.create(user=user,
                                       year=current_year,
                                       month=current_month,
                                       leave_type=leave,
                                       days=leave.count,
                                       status_action_by=admin,
                                       comments="monthly leave credit given by admin")
            leave_entry.balance = leave.count
            leave_entry.applied = 0
            leave_entry.approved = 0
            leave_entry.save()


def yearly_leave_type_addition(user, leave):
    admin = User.objects.get(id=35)
    current_year = date.today().year
    current_month = date.today().month
    leave_entry, created = LeaveSummary.objects.get_or_create(user=user,
                                                              year=current_year,
                                                              leave_type=leave)
    if leave_entry:
        CreditEntry.objects.create(user=user,
                                   year=current_year,
                                   month=current_month,
                                   leave_type=leave,
                                   days=leave.count,
                                   status_action_by=admin,
                                   comments="Yearly leave credit given by admin")
        leave_entry.balance = leave.count
        leave_entry.applied = 0
        leave_entry.approved = 0
        leave_entry.save()


def regular_leave_type_addition(user, leave):
    current_year = date.today().year
    leave_entry, created = LeaveSummary.objects.get_or_create(user=user,
                                                              year=current_year,
                                                              leave_type=leave)
    if leave_entry:
        leave_entry.balance = 0
        leave_entry.applied = 0
        leave_entry.approved = 0
        leave_entry.save()