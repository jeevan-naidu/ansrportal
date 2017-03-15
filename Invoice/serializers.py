from rest_framework import serializers
from models import Invoice, InvoiceTransaction
from Leave.views import AllowedFileTypes


class InvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, default='')
    reason = serializers.CharField(max_length=1000,
                                   default='',
                                   style={'base_template': 'textarea.html', 'rows': 10}
                                   )
    amount = serializers.IntegerField()

    class Meta:
        model = Invoice
        fields = ('id', 'title', 'reason', 'amount', 'ppl_involved', 'atachement')

    def saveas(self, request):

        attachment = request.FILES.get('atachement', "")
        if attachment:
            if attachment.name.split(".")[-1] not in AllowedFileTypes:
                file = None
            else:
                file = attachment
        else:
            file = None
        title = self.validated_data['title']
        reason = self.validated_data['reason']
        amount = self.validated_data['amount']
        invoice = Invoice.objects.create(title=title,
                                         reason=reason,
                                         amount=amount,
                                         user=request.user,
                                         atachement=file)

        invoice.save()
        for val in self.validated_data['ppl_involved']:
            invoice.ppl_involved.add(val)
        invoice.save()


class InvoiceTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceTransaction
        fields = ('reason', 'status')

    def save_as(self, role, request, pk):
        InvoiceTransaction(
            status=self.validated_data['status'],
            reason=self.validated_data['reason'],
            approved_by=request.user,
            invoice_id=pk,
            role=role
        ).save()

    @staticmethod
    def transactions(pk, role):
        transaction = InvoiceTransaction.objects.filter(invoice_id=pk,
                                                        role=role).order_by('id')
        if transaction:
            return InvoiceTransactionSerializer(transaction[0])
        else:
            return InvoiceTransactionSerializer()

