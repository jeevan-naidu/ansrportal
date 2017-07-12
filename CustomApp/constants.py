"""Place where we can register our app and change the available status """

REQUEST_IDENTIFIER = 'Initial'

"""Request status for user"""
REQUEST_STATUS = (
    ('Initiated', 'Initiated'),
    ('Withdrawn', 'Withdrawn'),
    ('Completed', 'Completed')
)

"""Task final status"""
TASK_STATUS = (
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Rolled Back', 'Rolled Back'),
    ('Completed', 'Completed')
)

"""Process approval flags available for action"""
PROCESS_STATUS = (
    ('approve', 'Approve'),
    ('reject', 'Reject')
)

"""Money Approval flags available for action"""
PAYMENT_STATUS = (
    ('yes', 'Yes'),
    ('no', 'No')
)


""" All the registered apps using framework"""
WORKFLOW_APPS = [
    'Reimburse',
    'Invoice',
    'LaptopAvail'
]