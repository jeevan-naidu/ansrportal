from django.shortcuts import render, HttpResponse
from models import LaptopApply
from django.views.generic import View
# Create your views here.


class LaptopReturn(View):
    template_name = "return_list.html"
    queryset = LaptopApply.objects.select_related('user').filter(return_status='initiated',
                                                                 process_status='Completed')
    queryset_admin = LaptopApply.objects.select_related('user').filter(return_status="returned",
                                                                       laptop__avaliable=False)

    def get(self, request):
        return_laptop_id = request.GET.get('id')
        approve_laptop_id = request.GET.get('approve_id')
        if return_laptop_id:
            laptop_entry = self.queryset.get(id=return_laptop_id)
            laptop_entry.return_status = "returned"
            laptop_entry.save()
        if approve_laptop_id and self.request.user.groups.filter(name="LaptopAdmin").exists():
            laptop_entry = self.queryset_admin.get(id=approve_laptop_id)
            laptop_entry.laptop.avaliable = True
            laptop_entry.return_status = "approved"
            laptop_entry.laptop.save()
            laptop_entry.save()
        queryset = self.queryset.filter(user=request.user)
        queryset_admin = self.queryset_admin.all()
        return render(request, self.template_name, {'queryset': queryset, 'queryset_admin': queryset_admin})




