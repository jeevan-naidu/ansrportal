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

""" All the registered apps using framework"""
WORKFLOW_APPS = [
    'Reimburse',
    'Invoice',
    'LaptopAvail'
]