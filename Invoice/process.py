from Invoice.models import Invoice, Transaction, Payment
from Invoice.serializers import InvoiceSerializer, TransactionSerializer, FinanceSerializer
from helpers import manager, hr

"""
Process dicti
"""
PROCESS = {
    'invoice_raise': {
        'name': 'Raising For Invoice',
        'model': Invoice,
        'role': 'submitter',
        'method': manager,
        'serializer': InvoiceSerializer,
        'transitions': ['finance_approval', None]
    },
    'finance_approval': {
        'name': 'Finance Approval',
        'model': Transaction,
        'role': 'Finance',
        'method': hr,
        'serializer': TransactionSerializer,
        'transitions': ['payment_recieved', 'invoice_raise']
    },
    'payment_recieved': {
        'name': 'Payment Recieved',
        'model': Payment,
        'role': 'Finance',
        'method': manager,
        'serializer': FinanceSerializer,
        'transitions': [None, 'payment_recieved']
    },

}

INITIAL = 'invoice_raise'

LIST_VIEW = ["milestone_date", "milestone_name", "user", 'process_status', "description", 'closed_on_date',
             'amount', "project", ]
DETAIL_VIEW = ["milestone_date", "milestone_name", "user", 'process_status', 'request_status',
               "description", 'closed_on_date', 'amount', "project", ]
TITLE = 'Invoice for ANSR Source'
DESCRIPTION = 'Invoice Process '
