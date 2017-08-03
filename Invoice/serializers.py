
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
            invoice_id=pk,
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


