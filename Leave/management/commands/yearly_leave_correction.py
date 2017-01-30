from django.contrib.auth.models import User
from Leave.models import CreditEntry, LeaveSummary, LeaveType, LeaveApplications
from datetime import date
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
        if leave.id == 1:
            monthly_leave_type_addition(user, leave)
        elif leave.id == 9:
            comp_off_carry_forward(user, leave)


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
        leave_applied_current_year = LeaveApplications.objects.filter(user=user,
                                                                      leave_type=leave,
                                                                      applied_on__lte=date(day=17,
                                                                                           month=1,
                                                                                           year=current_year),
                                                                      from_date__gte=date(day=1,
                                                                                          month=1,
                                                                                          year=date.today().year))
        for applied_leave in leave_applied_current_year:
            applied_leave_balance += float(applied_leave.days_count)
            if applied_leave.status == 'open':
                applied_leave_applied += float(applied_leave.days_count)
            elif applied_leave.status == 'approved':
                applied_leave_approved += float(applied_leave.days_count)
        if earned_leave + applied_leave_balance > 45:
            adjustment = (earned_leave + applied_leave_balance) - 45
            adjustment *= -1
            earned_leave += float(adjustment)
            CreditEntry.objects.create(user=user,
                                       year=current_year,
                                       month=current_month,
                                       leave_type=leave,
                                       days=adjustment,
                                       status_action_by=admin,
                                       comments="Year end adjustment by system for leave greater than 45")
        record, created = LeaveSummary.objects.get_or_create(user=user,
                                                             year=current_year,
                                                             leave_type=leave
                                                             )
        if record:
            current_year_applied_leave = float(record.applied) + float(record.approved)
            record.balance = (earned_leave + 1.5) - current_year_applied_leave
            record.save()


def comp_off_carry_forward(user, leave):
    admin = User.objects.get(id=35)
    current_year = date.today().year
    current_month = date.today().month
    previous_year = current_year - 1
    comp_off_balance = LeaveSummary.objects.filter(user=user,
                                                   leave_type=leave,
                                                   year=previous_year)
    if comp_off_balance:
        record, created = LeaveSummary.objects.get_or_create(user=user,
                                                             year=current_year,
                                                             leave_type=leave,
                                                             )
        if record and not created:
            CreditEntry.objects.create(user=user,
                                       year=current_year,
                                       month=current_month,
                                       leave_type=leave,
                                       days=comp_off_balance.balance,
                                       status_action_by=admin,
                                       comments="comp_off avail balance carry forward")
            record.balance = float(record.balance) + float(comp_off_balance.balalnce)
            record.save()


