# https://stackoverflow.com/questions/22250352/programmatically-create-a-django-group-with-permissions
# https://docs.djangoproject.com/en/4.0/howto/custom-management-commands/
import logging
import os

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from auctions import models

# Add logger
logger_groups_policy = logging.getLogger('management/commands/groups_policy')
f_handler = logging.FileHandler('general.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger_groups_policy.addHandler(f_handler)
logger_groups_policy.setLevel(os.getenv('DJANGO_LOG_LEVEL'))


# https://stackoverflow.com/questions/25024795/django-1-7-where-to-put-the-code-to-add-groups-programmatically
class Command(BaseCommand):
    def handle(self, *args, **options):
        logger_groups_policy.debug("Create permissions.")

        # Moderator can add, delete, view, change comments
        moderators_ct = ContentType.objects.get_for_model(models.Comments)
        moderators_perm = list(Permission.objects.filter(content_type=moderators_ct))

        # Auction admins can add, delete, view, change Category, Info_msg,
        # Can delete, view listing
        # Can delete and view bids
        auctions_admins_perm = [
            *list(Permission.objects.filter(content_type=ContentType.objects.get_for_model(models.Category))),
            *list(Permission.objects.filter(content_type=ContentType.objects.get_for_model(models.Info_msg))),
            Permission.objects.get(codename='delete_listing'),
            Permission.objects.get(codename='view_listing'),
            Permission.objects.get(codename='view_bids'),
            Permission.objects.get(codename='delete_bids')
        ]

        # Create groups
        groups = {'Auctions_admins': auctions_admins_perm,
                  'Moderators': moderators_perm
                  }

        logger_groups_policy.debug("Create groups.")
        for group in groups:
            new_group, created = Group.objects.get_or_create(name=group)
            for permission in groups[group]:
                new_group.permissions.add(permission)

        logger_groups_policy.debug("Create users (moderator and admin).")
        # Create user (User swapped with auctions.User)
        user = models.User.objects.create_user(username='moderator',
                                               is_staff=True,
                                               password=os.getenv('DJANGO_MODERATOR_PASSWD')
                                               )
        logger_groups_policy.debug("Add user to moderator group.")
        # Add user to group
        group = Group.objects.get(name='Moderators')
        group.user_set.add(user)
        user.save()
        # Create superuser
        user = models.User.objects.create_superuser('admin',
                                                    password=os.getenv('DJNAGO_admin_PASSWD'))
        user.save()
