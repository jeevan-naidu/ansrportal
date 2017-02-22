from rest_framework import serializers
from models import Invoice, InvoiceTransaction


class InvoiceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, default='')
    reason = serializers.CharField(max_length=100, default='')
    amount = serializers.IntegerField()

    class Meta:
        model = Invoice
        fields = ('id', 'title', 'reason', 'amount', 'ppl_involved')

    def saveas(self, request):
        title = self.validated_data['title']
        reason = self.validated_data['reason']
        amount = self.validated_data['amount']
        invoice = Invoice.objects.create(title=title,
                                         reason=reason,
                                         amount=amount,
                                         user=request.user)
        invoice.save()
        for val in self.validated_data['ppl_involved']:
            invoice.ppl_involved.add(val)


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


