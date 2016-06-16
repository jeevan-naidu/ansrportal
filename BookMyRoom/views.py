from django.shortcuts import render
from models import RoomDetail
from django.template.loader import render_to_string
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

# Create your views here.
TimingsList = [ ['08:00-08:30', '08:30-09:00', '09:00-09:30', '09:30-10:00'],
                ['10:00-10:30', '10:30-11:00', '11:00-11:30', '11:30-12:00'],
                ['12:00-12:30', '12:30-13:00', '13:00-13:30', '13:30-14:00'],
                ['14:00-14:30', '14:30-15:00', '15:00-15:30', '15:30-16:30'],
                ['16:30-17:00', '17:00-17:30', '17:30-18:00', '18:00-18:30'],
                ['18:30-19:00', '19:00-19:30', '19:30-20:00', '20:00-20:30'] ] 

def index(request):
    return render(request, 'BookMyRoom/index.html')

def GetBookingsView(request):
    
    import ipdb;ipdb.set_trace()
    context_data = {"html_data": "", "rooms_list": [1,2,3,4,5], "bookings_list": [], 'TimingsList': TimingsList, "for_date":"2016-06-15"}
    for_date = '2016-06-15'
    location = request.POST.get("location")
    context_data['rooms_list'] = RoomDetail.objects.filter(active=True)
    bookings_list = []
    
    context_data['success_msg'] = "Your grievance has been submitted successfully. A person from the HR department will get back to you shortly."
    template = render(request, 'BookMyRoom/BookRoomAndViewDetails.html', context_data)
    context_data['html_data'] = template.content
    context_data.pop('rooms_list')
    return JsonResponse(context_data)
    
