from Reimburse.models import Reimburse, Transaction
from Reimburse.serializers import ReimburseSerializer, TransactionSerializer
from helpers import manager, hr


PROCESS = {
    'reimburse_raise': {
        'name': 'Raising For Reimbursement',
        'model': Reimburse,
        'role': 'submitter',
        'method': manager,
        'serializer': ReimburseSerializer,
        'transitions': ['manager_approval', None]
    },
    'manager_approval': {
        'name': 'Manager Approval',
        'model': Transaction,
        'role': 'Manager',
        'method': manager,
        'serializer': TransactionSerializer,
        'transitions': ['finance_approval', 'reimburse_raise']
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

INITIAL = 'reimburse_raise'

DETAIL = ["bill_no", "bill_date", "vendor_name", 'nature_of_expenses', 'amount', 'user', 'attachment']
TITLE = 'Reimbursement for ANSR Source'
DESCRIPTION = 'Reimbursement Process '
