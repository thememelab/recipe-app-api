import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError  # Add this import
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('waiting for database...')
        db_up = False
        while db_up is False:
            try:
                # Directly check if the database is available
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                # If database is unavailable, print a message and wait 1 second
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        # Once the loop breaks (database is available), print success message
        self.stdout.write(self.style.SUCCESS('Database available'))
