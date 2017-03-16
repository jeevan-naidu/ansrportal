from rest_framework import serializers
from models import Reimburse, Transaction
from Leave.views import AllowedFileTypes


class ReimburseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    bill_no = serializers.CharField(max_length=100, default='',
                                    style={'base_template': 'rest_framework/custom_input.html'})
    bill_date = serializers.DateField(input_formats=None,
                                      style={'base_template': 'rest_framework/custom_datepicker.html'})
    vendor_name = serializers.CharField(max_length=100, default='',
                                        style={'base_template': 'rest_framework/custom_input.html'})
    nature_of_expenses = serializers.CharField(max_length=1000,
                                   default='',
                                   style={'base_template': 'rest_framework/custom_textarea.html', 'rows': 5})
    amount = serializers.IntegerField(style={'base_template': 'rest_framework/custom_input.html'})
    attachment = serializers.FileField(max_length=None, allow_empty_file=True,
                                       style={'base_template': 'rest_framework/custom_attach.html'})

    class Meta:
        model = Reimburse
        fields = ('id', 'bill_no', 'bill_date', 'vendor_name', 'nature_of_expenses', 'amount', 'attachment')

    def save_as(self, request):
        bill_no = self.validated_data['bill_no']
        bill_date = self.validated_data['bill_date']
        vendor_name = self.validated_data['vendor_name']
        nature_of_expenses = self.validated_data['nature_of_expenses']
        amount = self.validated_data['amount']
        attachment = request.FILES.get('attachment', "")
        func = lambda attachment : attachment if attachment.name.split(".")[-1]  in AllowedFileTypes else None
        file = func(attachment)
        Reimburse(bill_no=bill_no,
                  bill_date=bill_date,
                  vendor_name=vendor_name,
                  attachment=file,
                  nature_of_expenses=nature_of_expenses,
                  amount=amount,
                  user=request.user).save()



class TransactionSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=1000,
                                   style={'base_template': 'textarea.html', 'rows': 4}
                                   )
    class Meta:
        model = Transaction
        fields = ('status','reason')

    def save_as(self, role, request, pk):
        Transaction(
            status=self.validated_data['status'],
            reason=self.validated_data['reason'],
            approved_by=request.user,
            reimburse_id=pk,
            role=role
        ).save()

    @staticmethod
    def transactions(pk, role):
        transaction = Transaction.objects.filter(reimburse_id=pk,
                                                 role=role).order_by('-id')
        if transaction:
            return TransactionSerializer(transaction[0])
        else:
            return TransactionSerializer()


