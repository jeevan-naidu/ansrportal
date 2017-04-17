"""Place where we can register our app and change the available status """

REQUEST_IDENTIFIER = 'Initial'

REQUEST_STATUS = (
    ('Initiated', 'Initiated'),
    ('Withdrawn', 'Withdrawn'),
    ('Completed', 'Completed')
)

TASK_STATUS = (
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Rolled Back', 'Rolled Back'),
    ('Completed', 'Completed')
)

PROCESS_STATUS = (
    ('approve', 'Approve'),
    ('reject', 'Reject')
)
WORKFLOW_APPS = [
    'Reimburse',
    'Invoice',
    'LaptopAvail',
]