from rest_framework import serializers
from models import Reimburse, Transaction


class ReimburseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, default='')
    reason = serializers.CharField(max_length=1000,
                                   default='',
                                   style={'base_template': 'textarea.html', 'rows': 10})
    amount = serializers.IntegerField()

    class Meta:
        model = Reimburse
        fields = ('id', 'title', 'reason', 'amount')

    def saveas(self, request):
        title = self.validated_data['title']
        reason = self.validated_data['reason']
        amount = self.validated_data['amount']
        Reimburse(title=title,
                  reason=reason,
                  amount=amount,
                  user=request.user).save()


class TransactionSerializer(serializers.ModelSerializer):
    reason = serializers.CharField(max_length=1000,
                                   style={'base_template': 'textarea.html', 'rows': 4}
                                   )
    class Meta:
        model = Transaction
        fields = ('reason', 'status')

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
                                                 role=role).order_by('id')
        if transaction:
            return TransactionSerializer(transaction[0])
        else:
            return TransactionSerializer()


