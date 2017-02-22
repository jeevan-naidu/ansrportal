from Invoice.models import Invoice, InvoiceTransaction
from Invoice.serializers import InvoiceSerializer, InvoiceTransactionSerializer
from helpers import manager


PROCESS = {
    'reimburse_raise': {
        'name': 'Raising For Reimbursement',
        'model': Invoice,
        'role': 'submitter',
        'method': manager,
        'serializer': InvoiceSerializer,
        'transitions': ['manager_approval', None]
    },
    'manager_approval': {
        'name': 'Manager Approval',
        'model': InvoiceTransaction,
        'role': 'Reviewer',
        'method': manager,
        'serializer': InvoiceTransactionSerializer,
        'transitions': ['finance_approval', 'reimburse_raise']
    },
    'finance_approval': {
        'name': 'Finance Approval',
        'model': InvoiceTransaction,
        'role': 'Final',
        'method': manager,
        'serializer': InvoiceTransactionSerializer,
        'transitions': ['bala_approval', 'manager_approval']
    },
'bala_approval': {
        'name': 'Bala Approval',
        'model': InvoiceTransaction,
        'role': 'Final',
        'method': manager,
        'serializer': InvoiceTransactionSerializer,
        'transitions': [None, 'finance_approval']
    },

}

INITIAL = 'reimburse_raise'

DETAIL = ["title", "reason", "amount", "user"]
TITLE = 'Reimbursement for ANSR Source'
DESCRIPTION = 'Reimbursement Process '
