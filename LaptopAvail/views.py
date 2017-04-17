from django.shortcuts import render, HttpResponse
from models import Laptops, Laptop, Transaction
from employee.models import Employee
# Create your views here.

def LaptopReturn(request):

    if request.method == 'GET':
        # import ipdb; ipdb.set_trace()
        user = request.user
        reportee = Employee.objects.all()
        if not reportee:
            laptops = Laptop.objects.filter(user_id=user.employee.user_id)
            laptop_lists = []
            laptop_dict = {'id': '', 'from_date': '', 'to_date': '', 'laptop': '', 'process_status': '', 'reason': ''}
            for laptop in laptops:
                laptop_id = laptop.id
                id = laptop_id
                laptop_user = Laptop.objects.get(laptop_id=laptop.laptop_id)
                if laptop_user.process_status == 'completed' or laptop_user.process_status == 'Return in progess':
                    laptop_dict['id'] = id
                    laptop_dict['process_status'] = laptop_user.process_status
                    laptop_dict['laptop'] = laptop_user.laptop
                    laptop_dict['from_date'] = laptop_user.from_date
                    laptop_dict['to_date'] = laptop_user.to_date
                    laptop_dict['reason'] = laptop_user.reason
                    laptop_lists.append(laptop_dict)
                    laptop_dict = {'id': '', 'from_date': '', 'to_date': '', 'laptop': '', 'process_status': '',
                                   'reason': ''}
        else:
            laptop_lists = []
            laptop_dict = {'id': '', 'from_date': '', 'to_date': '', 'laptop': '', 'process_status': '', 'reason': ''}
            for user in reportee:
                laptops = Laptop.objects.filter(user_id=user.user_id)
                for laptop in laptops:
                    laptop_id = laptop.id
                    id = laptop_id
                    laptop_user = Laptop.objects.get(laptop_id=laptop.laptop_id)
                    if laptop_user.process_status == 'completed' or laptop_user.process_status == 'Return in progess':
                        laptop_dict['id'] = id
                        laptop_dict['process_status'] = laptop_user.process_status
                        laptop_dict['laptop'] = laptop_user.laptop
                        laptop_dict['from_date'] = laptop_user.from_date
                        laptop_dict['to_date'] = laptop_user.to_date
                        laptop_dict['reason'] = laptop_user.reason
                        laptop_lists.append(laptop_dict)
                        laptop_dict = {'id': '', 'from_date': '', 'to_date': '', 'laptop': '', 'process_status': '',
                                       'reason': ''}

    return render(request, 'return.html', {'laptop_lists':laptop_lists})

def return_apply(request):

    if request.method == 'GET':
        # import ipdb; ipdb.set_trace()
        id = request.GET['id']
        laptops = Laptop.objects.get(id=id)
        if laptops.process_status != "Return in progess":
            laptops.process_status = "Return in progess"
            laptops.save()
            return HttpResponse('success')

def return_approve(request):

    if request.method == 'GET':
        # import ipdb; ipdb.set_trace()
        id = request.GET['id']
        laptops = Laptop.objects.get(id=id)
        laptop = Laptops.objects.get(id = laptops.laptop_id)
        if laptop.avaliable == False:
            laptop.avaliable = "True"
            laptop.save()
        if laptops.process_status == "Return in progess":
            laptops.process_status = "Completed"
            laptops.save()
            return HttpResponse('success')
