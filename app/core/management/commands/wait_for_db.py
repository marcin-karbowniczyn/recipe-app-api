""" Django command to wait for the DB to be available """
import time

# The error that's thrown from the Psycopg2 package sometimes when the DB isn't ready
from psycopg2 import OperationalError as Psycopg2OpError
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ Django command to wait for the DB """

    # This method will check if the DB is ready, next up it will finish its execution and allow next commands to be executed (see in docker-compose)
    # This method is obligatory. It gets called every time we run our django commands, in this case wait_for_db
    def handle(self, *args, **options):
        """ Entrypoint for command """
        # Standard output that we can use to log things to the CLI
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])  # If DB isn't ready, it will throw an exception, so it will move to the except block
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database available!'))
