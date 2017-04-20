from django.shortcuts import render, HttpResponse
from models import Laptops, Laptop, Transaction
from employee.models import Employee
# Create your views here.

def LaptopReturn(request):

    if request.method == 'GET':
        laptop_lists = []
        if request.user.groups.filter(name__in=['BookingRoomAdmin']).exists():
            reportee = Employee.objects.all()
            for user in reportee:
                laptop_dict = {}
                laptops = Laptop.objects.filter(user_id=user.user_id)
                for laptop in laptops:
                    laptop_id = laptop.id
                    laptop_user = Laptop.objects.filter(laptop_id=laptop.laptop_id)
                    for laptop in laptop_user:
                        if laptop.process_status == 'completed' or laptop.process_status == 'Completed' or laptop.process_status == 'Return in progress':
                            laptop_dict['user'] = laptop.user
                            laptop_dict['id'] = laptop_id
                            laptop_dict['process_status'] = laptop.process_status
                            laptop_dict['laptop'] = laptop.laptop
                            laptop_dict['from_date'] = laptop.from_date
                            laptop_dict['to_date'] = laptop.to_date
                            laptop_dict['reason'] = laptop.reason
                            laptop_dict['username'] = laptop.user.first_name + ' ' + laptop.user.last_name
                            laptop_lists.append(laptop_dict)
        else:
            laptop_dict = {}
            laptops = Laptop.objects.filter(user_id=request.user.id)
            for laptop in laptops:
                if laptop.process_status == 'completed' or laptop.process_status == 'Completed' or laptop.process_status == 'Return in progress':
                    laptop_dict['user'] = laptop.user
                    laptop_dict['id'] = laptop.id
                    laptop_dict['process_status'] = laptop.process_status
                    laptop_dict['laptop'] = laptop.laptop
                    laptop_dict['from_date'] = laptop.from_date
                    laptop_dict['to_date'] = laptop.to_date
                    laptop_dict['reason'] = laptop.reason
                    laptop_dict['username'] = laptop.user.first_name + ' ' + laptop.user.last_name
                    laptop_lists.append(laptop_dict)

    return render(request, 'return.html', {'laptop_lists':laptop_lists})

def return_apply(request):

    if request.method == 'GET':
        id = request.GET['id']
        try:
            laptops = Laptop.objects.get(id=id)
            if laptops.process_status != "Return in progress":
                laptops.process_status = "Return in progress"
                laptops.save()
                return HttpResponse('success')
        except Laptop.DoesNotExist:
            return render(request, 'return.html', {})


def return_approve(request):

    if request.method == 'GET':
        if request.user.groups.filter(name__in=['BookingRoomAdmin']).exists():
            id = request.GET['id']
            laptops = Laptop.objects.get(id=id)
            laptop = Laptops.objects.get(id = laptops.laptop_id)
            if laptop.avaliable == False:
                laptop.avaliable = "True"
                laptop.save()
            if laptops.process_status == "Return in progress":
                laptops.process_status = "Completed"
                laptops.save()
                return HttpResponse('success')
