from django.db.models.signals import pre_save
from django.dispatch import receiver
from employee.models import Employee

# method for updating
@receiver(pre_save, sender=Employee)
def update_color(sender, instance, **kwargs):
    color_list = ['violet', 'indigo', 'blue', 'green', 'yellow', 'orange', 'red']
    colorindex = int(instance.user_id) % 7
    color = color_list[colorindex]
    instance.color = color




