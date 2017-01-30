from rest_framework import serializers
from models import Reimburse, Transaction


class ReimburseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100, default='')
    reason = serializers.CharField(max_length=100, default='')
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
    class Meta:
        model = Transaction
        fields = ('reason',)

    def save_as(self, role, request, pk, status):
        Transaction(
            status=status,
            reason=self.validated_data['reason'],
            approved_by=request.user,
            reimburse_id=pk,
            role=role
        ).save()


