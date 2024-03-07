""" test custom Django managment commands """
from unittest.mock import patch
from psycopg2 import OperationalError as Psycopg2Error

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import SimpleTestCase


# check method of a BaseCommand checks the status of the DB. We mock this check method to simulate the response.
@patch('core.management.commands.wait_for_db.Command.check')
class CommandTests(SimpleTestCase):
    """ Test commands """

    # Every method needs to start with test for the testing system to notice it
    def test_wait_for_db_available(self, patched_check):  # patched_check is an argument added by the patch decorator
        """ Test waiting for database if database is ready """
        patched_check.return_value = True

        call_command('wait_for_db')
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep, patched_check):
        """ Test waiting for database when getting OperationalError """
        # The first two times we call the mocked method (check) we want to raise Psycopg2Error, next three times OperationalError and one time True.
        patched_check.side_effect = [Psycopg2Error] * 2 + [OperationalError] * 3 + [True]
        call_command('wait_for_db')
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])
