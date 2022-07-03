# https://stackoverflow.com/questions/22250352/programmatically-create-a-django-group-with-permissions
# https://docs.djangoproject.com/en/4.0/howto/custom-management-commands/
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from auctions import models

# Add logger
logger = logging.getLogger('management/commands/create_default_categories')
f_handler = logging.FileHandler('general.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
logger.setLevel(os.getenv('DJANGO_LOG_LEVEL'))


# https://stackoverflow.com/questions/25024795/django-1-7-where-to-put-the-code-to-add-groups-programmatically
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger.debug("Create default categories.")

        # Create categories
        categories = ('clothes',
                      'shoes',
                      'bijouterie',
                      'accessories',
                      'others')

        for name in categories:
            category = models.Category(name=name)
            category.save()

