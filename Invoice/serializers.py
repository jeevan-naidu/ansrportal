
from rest_framework import serializers
from models import Invoice, Transaction
from Leave.views import AllowedFileTypes


class InvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    milestone_date = serializers.DateField(input_formats=None,
                                      style={'base_template': 'rest_framework/custom_datepicker.html'})
    amount = serializers.IntegerField(style={'base_template': 'rest_framework/custom_input.html'})

    class Meta:
        model = Invoice
        fields = ('id', 'milestone_date', 'amount')

    # def save_as(self, request):
    #     bill_no = self.validated_data['id']
    #     bill_date = self.validated_data['bill_date']
    #     vendor_name = self.validated_data['vendor_name']
    #
    #     Invoice(bill_no=bill_no,
    #               bill_date=bill_date,
    #               vendor_name=vendor_name,
    #               attachment=file,
    #               nature_of_expenses=nature_of_expenses,
    #               amount=amount,
    #               user=request.user).save()



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
        transaction = Transaction.objects.filter(invoice_id=pk,
                                                 role=role).order_by('-id')
        if transaction:
            return TransactionSerializer(transaction[0])
        else:
            return TransactionSerializer()


