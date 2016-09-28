from django.db import models
from django.contrib.auth.models import User
import hashlib
from django.utils import timezone

RESULT_STATUS = (('applied', 'Applied'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('returned', 'Returned'))
BOOK_STATUS = (('available', 'Available'), ('unavailable', 'UnAvailable'))

class Book(models.Model):
    """
    An Book class - to describe book in the system.
    """
    title = models.CharField(max_length=200)
    ISBN = models.CharField(max_length=200)
    genre = models.CharField(max_length=200)
    publisher = models.ForeignKey('Publisher')
    author = models.ForeignKey('Author')
    lend_period = models.ForeignKey('LendPeriods')
    page_amount = models.IntegerField()
    status = models.CharField(max_length=20, choices=BOOK_STATUS, verbose_name='book_status')

    def __unicode__(self):
        return 'Book: ' + self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Book"
        verbose_name_plural = "Books"


class LendPeriods(models.Model):
    """
    Users can borrow books from library for different
    time period. This class defines frequently-used
    lending periods.
    """
    name = models.CharField(max_length=50)
    days_amount = models.IntegerField()

    def __unicode__(self):
        return '%s' % self.name

    class Meta:
        get_latest_by = "days_amount"
        ordering = ['days_amount']
        verbose_name = "Lending period"
        verbose_name_plural = "Lending periods"


class Publisher(models.Model):
    """
    Class defines book's publisher
    """
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Publisher: %s' % self.name

    class Meta:
        get_latest_by = "name"
        ordering = ['name']
        verbose_name = "Publisher"
        verbose_name_plural = "Publishers"


class Author(models.Model):
    """
    Class defines book's author
    """
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

    def __unicode__(self):
        return 'Author: ' + self.name + ' ' + self.surname

    def __str__(self):
        return 'Author: ' + self.name + ' ' + self.surname

    class Meta:
        get_latest_by = "name"
        ordering = ['name', 'surname']
        verbose_name = "Author"
        verbose_name_plural = "Authors"


class BookApplication(models.Model):
    """
    class defines book transactions
    """
    book = models.ForeignKey('Book')
    lend_by = models.ForeignKey(User)
    lend_from = models.DateField()
    lend_to = models.DateField()
    status = models.CharField(max_length=20, choices=RESULT_STATUS, verbose_name='application_status')
    status_action_by = models.ForeignKey(User, related_name="action_taken_by")
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateField(auto_now=True)

    def __unicode__(self):
        return 'User: ' + self.lend_by.First_name + ' ' + self.lend_by.Last_name

    def __str__(self):
        return 'User: ' + self.lend_by.First_name + ' ' + self.lend_by.Last_name

    class Meta:
        get_latest_by = "-modified_on"
        ordering = ['-modified_on','status']
        verbose_name = "BookApplication"
        verbose_name_plural = "BookApplications"





