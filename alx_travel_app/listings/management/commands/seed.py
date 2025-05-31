from django.core.management.base import BaseCommand
from listings.models import Listing
import random

class Command(BaseCommand):
    help = 'Seed the database with sample listings'

    def handle(self, *args, **kwargs):
        Listing.objects.all().delete()

        locations = ['Paris', 'New York', 'Tokyo', 'London', 'Cairo']
        for i in range(10):
            Listing.objects.create(
                title=f'Sample Listing {i + 1}',
                description='A great place to stay.',
                price_per_night=random.uniform(50, 300),
                location=random.choice(locations),
                available=True
            )
        self.stdout.write(self.style.SUCCESS('Successfully seeded listings.'))
