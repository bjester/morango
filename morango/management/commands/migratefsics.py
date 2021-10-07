import logging
from django.core.management.base import BaseCommand
from morango.models import TransferSession


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrates the fsics data on fields of TransferSession into their own table"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            action="store",
            type=int,
            default=10,
            help="Maximum number of transfer sessions for which to migrate fsics",
        )

    def handle(self, *args, **options):
        transfer_sessions = TransferSession.objects.exclude(
            client_fsic="{}", server_fsic="{}"
        )

        for transfer_session in transfer_sessions[:options["limit"]]:
            logger.info("Migrating transfer session {}".format(transfer_session.id))
            transfer_session.load_fsics(do_save=True)
