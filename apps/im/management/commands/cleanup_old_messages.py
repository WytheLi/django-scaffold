from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from im.models import Message


class Command(BaseCommand):
    help = "Clean up messages older than the retention period"

    def handle(self, *args, **options):
        retention_days = settings.MESSAGE_RETENTION_DAYS
        cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)

        deleted_count, _ = Message.objects.filter(timestamp__lt=cutoff_date).delete()

        self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} old messages"))
