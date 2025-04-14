
from unittest import TestCase
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError
from django.test import SimpleTestCase

@patch('core.management.commands.wait_for_db.Command.check')
class CommandTest(SimpleTestCase):

    def test_wait_for_db_ready(self, patched_check):        
        # Create a mock connection and set it for 'default' database
        patched_check.return_value = True
        print("Running wait_for_db command...")
        call_command('wait_for_db')  # Run the command
        # Ensure mock_getitem was called with 'default'
        patched_check.assert_called_once_with(databases=['default'])

    @patch('time.sleep')
    def test_wait_for_db_delay(self, patched_sleep , patched_check):
        # Simulate retries and finally return a mock connection
        patched_check.side_effect = [Psycopg2Error] * 2 + \
        [OperationalError] * 3 + [True]
        print("Running wait_for_db with delays...")
        call_command('wait_for_db')  # Run the command with retries
        # Ensure the mock was called 6 times (5 retries + 1 success)
        self.assertEqual(patched_check.call_count, 6)
        patched_check.assert_called_with(databases=['default'])

    
