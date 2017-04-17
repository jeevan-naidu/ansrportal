from Invoice.models import Invoice, Transaction
from Invoice.serializers import InvoiceSerializer, TransactionSerializer
from helpers import manager, hr


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
        'transitions': [None, 'invoice_raise']
    },

}

INITIAL = 'invoice_raise'

LIST_VIEW = ["milestone_date", "milestone_name", "user", 'process_status', "description",'closed_on_date',
             'amount', "project"]
DETAIL_VIEW = ["milestone_date", "milestone_name", "user", 'process_status', 'request_status',
               "description",'closed_on_date', 'amount', "project"]
TITLE = 'Invoice for ANSR Source'
DESCRIPTION = 'Invoice Process '
ATTACHMENT = False