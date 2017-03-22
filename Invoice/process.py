from Reimburse.models import Reimburse, Transaction
from Reimburse.serializers import ReimburseSerializer, TransactionSerializer
from helpers import manager, hr


PROCESS = {
    'invoice_raise': {
        'name': 'Raising For Reimbursement',
        'model': Reimburse,
        'role': 'submitter',
        'method': manager,
        'serializer': ReimburseSerializer,
        'transitions': ['manager_approval', None]
    },
    'finance_approval': {
        'name': 'Finance Approval',
        'model': Transaction,
        'role': 'Finance',
        'method': hr,
        'serializer': TransactionSerializer,
        'transitions': [None, 'manager_approval']
    },

}

INITIAL = 'invoice_raise'

LIST_VIEW = ["bill_no", "bill_date", "user", "vendor_name",'process_status', 'amount', 'attachment']
DETAIL_VIEW = ["bill_no", "bill_date", "user", "vendor_name", 'nature_of_expenses', 'amount', 'process_status',
               'request_status', 'attachment']
TITLE = 'Reimbursement for ANSR Source'
DESCRIPTION = 'Reimbursement Process '
