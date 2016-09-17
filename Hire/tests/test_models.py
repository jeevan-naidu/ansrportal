from django.test import TestCase
from Hire.models import Position, MRF, Profile, Process, Count
from django.contrib.auth.models import User
from django.utils import timezone

class PositionTest(TestCase):

    def create_position(self, department='media', designation='Editor', specialization='history'):
        return Position.objects.create(department=department, designation=designation, specialization=specialization)

    def test_position_creation(self):
        position = self.create_position()
        self.assertTrue(isinstance(position, Position))
        self.assertEqual(position.__unicode__(), position.department)


class MRFTest(TestCase):

    def create_MRF(self,position ,manager, requisition_number="editor/21/2015/hist",):
        return MRF.objects.create()

    def testMRF(self):
        position = Position.objects.create(id=1, department='media', designation='Editor', specialization='history')
        manager = User.objects.create(username='vivek')
        mrf = self.create_MRF(position, manager)
        self.assertTrue(isinstance(mrf, MRF))
        self.assertEqual(mrf.__unicode__(), MRF.requisition_number)
