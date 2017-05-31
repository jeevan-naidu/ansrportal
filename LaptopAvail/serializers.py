from rest_framework import serializers
from models import LaptopApply, Transaction, Laptops
from tasks import LaptopRaiseEmail


class LaptopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    laptop = serializers.ChoiceField(Laptops.objects.filter(avaliable=True),
                                     style={'base_template': 'rest_framework/custom_select.html'})
    from_date = serializers.DateField(input_formats=None,
                                      style={'base_template': 'rest_framework/custom_datepicker.html'})
    to_date = serializers.DateField(input_formats=None,
                                    style={'base_template': 'rest_framework/custom_datepicker.html'})
    reason = serializers.CharField(style={'base_template': 'rest_framework/custom_input.html'})

    class Meta:
        model = LaptopApply
        fields = ('id', 'from_date', 'to_date', 'reason', 'laptop')

    def get_laptop_id(self):
        return Laptops.object.filter(avaliable=True).values('laptop_id')

    def save_as(self, request):
        laptop = self.validated_data['laptop']
        from_date = self.validated_data['from_date']
        to_date = self.validated_data['to_date']
        reason = self.validated_data['reason']
        laptop_apply = LaptopApply.objects.create(laptop=laptop,
                                                  from_date=from_date,
                                                  to_date=to_date,
                                                  reason=reason,
                                                  user=request.user,
                                                  return_status='initiated')
        laptop.avaliable = False
        laptop.save()
        LaptopRaiseEmail.delay(laptop_apply, 'raise', laptop_apply.role, 'raise')


class TransactionSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=1000,
                                   style={'base_template': 'textarea.html', 'rows': 4},
                                   required=False
                                   )

    class Meta:
        model = Transaction
        fields = ('status', 'reason')

    def save_as(self, role, request, pk):
        laptop_apply = LaptopApply.objects.get(id=pk)
        if self.validated_data['status'] == 'reject':
            laptop_apply.laptop.avaliable = True
            laptop_apply.is_active = False
            laptop_apply.process_status = "Rolled Back"
            laptop_apply.laptop.save()
            laptop_apply.save()
        Transaction(
            status=self.validated_data['status'],
            reason=(lambda: self.validated_data['reason'] if 'reason' in self.validated_data else " ")(),
            approved_by=request.user,
            laptop_id=pk,
            role=role
        ).save()

       LaptopRaiseEmail.delay(laptop_apply, "transect", role, self.validated_data['status'])

    @staticmethod
    def transactions(pk, role):
        transaction = Transaction.objects.filter(laptop=pk,
                                                 role=role).order_by('-id')
        if transaction:
            return TransactionSerializer(transaction[0])
        else:
            return TransactionSerializer()


