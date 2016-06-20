from django.db import models
from django.contrib.auth.models import User
from CompanyMaster.models import OfficeLocation
# Create your models here.

LOCATION_CHOICES = (('karle_ground_floor', 'Karle-Ground Floor'), ('karle_second_floor', 'Karle-Second Floor'), ('btp', 'BTP'))
BOOKING_STATUS = (('booked', 'Booked'), ('cancelled', 'Cancelled'))

class RoomDetail(models.Model):
    
    room_name = models.CharField(max_length=100)
    location =  models.CharField(max_length = 100, choices=LOCATION_CHOICES)
    active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    
    def __unicode__(self):
        ''' return unicode strings '''
        return '%s' % (self.room_name + ": " + self.location)


class MeetingRoomBooking(models.Model):
    
    
    booked_by = models.ForeignKey(User)
    room = models.ForeignKey(RoomDetail)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    status = models.CharField(max_length = 100, choices=BOOKING_STATUS)
    # active = models.BooleanField(blank=False, default=True, verbose_name="Is Active?")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(verbose_name="last", auto_now=True)
    
    def __unicode__(self):
        ''' return unicode strings '''
        return '%s' % (self.booked_by.username + ": " + self.room.room_name)
    