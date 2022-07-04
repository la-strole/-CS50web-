import logging
import os

from django.contrib.auth.models import AbstractUser
from django.db import models

# Add logger
logger_models = logging.getLogger('models')
f_handler = logging.FileHandler('general.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger_models.addHandler(f_handler)
logger_models.setLevel(os.getenv('DJANGO_LOG_LEVEL'))


class User(AbstractUser):
    id = models.AutoField(editable=False,
                          primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timestamp = self.date_joined

    def __str__(self):

        return f'{self.get_username()}({self.get_full_name()})'


class Category(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True,
                          verbose_name="Category")

    name = models.CharField("Category name",
                            max_length=16,
                            help_text="Category name (max 16 characters)",
                            unique=True,
                            default='other')

    class Meta:
        db_table = 'category'
        verbose_name = 'Listing Category'
        verbose_name_plural = 'Listing Categories'

    def __str__(self):
        return self.name


class Listing(models.Model):
    id = models.AutoField(editable=False, primary_key=True)

    active = models.BooleanField(default=True, editable=False)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name="User id")
    # TODO Change CASCADE to set DEFAULT
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,
                                 verbose_name="Category")
    start_value = models.PositiveIntegerField("Start bet",
                                              help_text="Start bet (Integer value)")
    title = models.CharField("Title",
                             max_length=45,
                             help_text="Title (max 45 characters)")
    description = models.TextField("Description",
                                   max_length=120,
                                   help_text="Description (max 120 characters)")
    image_url = models.URLField("Image url",
                                max_length=120,
                                help_text="Image url (max 120 characters)",
                                blank=True)
    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listings'
        verbose_name_plural = 'Listings'

    def __str__(self):
        return f'{self.title} from {self.user}'

    @staticmethod
    def create_listing(kwargs: dict):
        try:
            listing = Listing(
                user=kwargs['user'],
                category=kwargs['category'],
                start_value=kwargs['start_value'],
                title=kwargs['title'],
                description=kwargs['description'],
                image_url=kwargs['image_url']
            )
            listing.save()
            return listing
        except (KeyError, ValueError) as e:
            logger_models.error(f"Can not create new listing. {e}, {type(e)}.")
            return None


class Wishlist(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name="User id")
    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                verbose_name="Listing id")

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'


class Comments(models.Model):
    id = models.BigAutoField(editable=False, primary_key=True)

    user = models.ForeignKey(User,
                             on_delete=models.SET('Deleted user'),
                             verbose_name="User id")
    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                verbose_name="Listing id")
    text = models.TextField("Comment",
                            max_length=120,
                            help_text="Comment (max 120 characters)")
    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)

    class Meta:
        db_table = 'comments'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'


class Bids(models.Model):
    id = models.BigAutoField(editable=False, primary_key=True)

    listing = models.ForeignKey(Listing,
                                on_delete=models.CASCADE,
                                verbose_name="Listing id")
    user = models.ForeignKey(User,
                             on_delete=models.SET('Deleted user'),
                             verbose_name="User id")
    value = models.PositiveIntegerField("New bid",
                                        help_text="Your bid")
    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)

    class Meta:
        db_table = 'bids'
        verbose_name = 'Bid'
        verbose_name_plural = 'Bids'


class Info_msg(models.Model):
    id = models.BigAutoField(editable=False, primary_key=True)

    is_read = models.BooleanField(default=False, editable=False)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name="User id")
    text = models.TextField(max_length=120, editable=False)
    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)

    class Meta:
        db_table = 'info_msg'
        verbose_name = 'Information message'
        verbose_name_plural = 'Information messages'
