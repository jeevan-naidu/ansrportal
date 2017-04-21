
from rest_framework import serializers
from models import Laptop, Transaction, Laptops
from Leave.views import AllowedFileTypes


class LaptopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    laptop = serializers.ChoiceField(Laptops.objects.filter(avaliable=True), style={'base_template': 'rest_framework/custom_select.html'})
    from_date = serializers.DateField(input_formats=None,
                                           style={'base_template': 'rest_framework/custom_datepicker.html'})
    to_date = serializers.DateField(input_formats=None,
                                      style={'base_template': 'rest_framework/custom_datepicker.html'})
    reason = serializers.CharField(style={'base_template': 'rest_framework/custom_input.html'})

    class Meta:
        model = Laptop
        fields = ('id', 'from_date', 'to_date', 'reason', 'laptop')

    def get_laptop_id(self):
        return Laptops.object.filter(avalible=True).values('laptop_id')

    def save_as(self, request):
        status = {"errors": "" , "success":"" }
        laptop = self.validated_data['laptop']
        from_date = self.validated_data['from_date']
        to_date = self.validated_data['to_date']
        reason = self.validated_data['reason']
        Laptop(laptop=laptop,
               from_date=from_date,
               to_date=to_date,
               reason=reason,
               user=request.user).save()
        laptop.avaliable = False
        laptop.save()

class TransactionSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=1000,
                                   style={'base_template': 'textarea.html', 'rows': 4},
                                   required=False
                                   )

    class Meta:
        model = Transaction
        fields = ('status', 'reason')

    def save_as(self, role, request, pk):
        Transaction(
            status=self.validated_data['status'],
            reason=(lambda: self.validated_data['reason'] if 'reason' in self.validated_data else " ")(),
            approved_by=request.user,
            laptop_id=pk,
            role=role
        ).save()

    @staticmethod
    def transactions(pk, role):
        transaction = Transaction.objects.filter(laptop=pk,
                                                 role=role).order_by('-id')
        if transaction:
            return TransactionSerializer(transaction[0])
        else:
            return TransactionSerializer()


