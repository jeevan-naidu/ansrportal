from django.apps import AppConfig


class EmployeeConfig(AppConfig):
    name = 'employee'
    verbose_name = 'Employee Information'

    def ready(self):
        import employee.signals
