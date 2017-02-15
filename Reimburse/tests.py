from django.test import TestCase
from Reimburse.models import Reimburse, Transaction
from django.contrib.auth.models import User


class ReimburseTestCase(TestCase):
    def setUp(self):
        # user = User.objects.create(id=1,
        #                            first_name="vivek",
        #                            last_name="pradhan",
        #                            email="vivek.pradhan@ansrsource.com",
        #                            password="P@ssword")
        Reimburse.objects.create(title="Travel to usa 1",
                                 reason="work for macgraw hill",
                                 amount=10000,
                                 user_id=543
                                 )
        Reimburse.objects.create(title="Team Lunch 2",
                                 reason="went for team lunch",
                                 amount=5000,
                                 user_id=543
                                 )

