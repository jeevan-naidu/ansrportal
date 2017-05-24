from LaptopAvail.models import LaptopApply, Transaction
from LaptopAvail.serializers import LaptopSerializer, TransactionSerializer
from helpers import manager, admin


PROCESS = {
    'laptop_avail_raise': {
        'name': 'Raising For Laptop',
        'model': LaptopApply,
        'role': 'submitter',
        'method': manager,
        'serializer': LaptopSerializer,
        'transitions': ['manager_approval', None]
    },
    'manager_approval': {
        'name': 'Manager Approval',
        'model': Transaction,
        'role': 'Manager',
        'method': manager,
        'serializer': TransactionSerializer,
        'transitions': ['admin_approval', 'laptop_avail_raise']
    },
    'admin_approval': {
        'name': 'Admin Approval',
        'model': Transaction,
        'role': 'Admin',
        'method': admin,
        'serializer': TransactionSerializer,
        'transitions': [None, 'manager_approval']
    },

}

INITIAL = 'laptop_avail_raise'
ATTACHMENT = False
LIST_VIEW = ["from_date", "to_date", "user", 'laptop', 'process_status', 'reason', ]
DETAIL_VIEW = ["from_date", "to_date", "user", 'laptop', 'reason',  "user", 'process_status', 'request_status',]
TITLE = 'Laptop for Work from home'
DESCRIPTION = 'Laptop Avail Process'