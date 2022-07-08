import logging
import os

from django.contrib.auth.models import AbstractUser
from django.db import models, IntegrityError

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

    @property
    def wishlist_count(self):
        result = len(self.wishlist_set.filter(listing__active=True))
        if result:
            return result
        else:
            return None

    def __str__(self):
        return f'{self.get_username()}'


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

    @property
    def get_current_bid(self):

        bids = Bids.objects.filter(listing=self)
        if not bids:
            return Bids(listing=self, user=self.user, value=self.start_value - 1)
        result = max(bids, key=lambda x: x.value)
        return result

    @property
    def comments(self):
        comments = self.comments_set.all()
        if comments:
            return comments
        else:
            return None

    class Meta:
        db_table = 'listings'
        verbose_name = 'Listings'
        verbose_name_plural = 'Listings'

    def __str__(self):
        return f'{self.title}'

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

    @staticmethod
    def raise_bid(data: dict):
        try:
            result = Bids(listing=data['listing'],
                          user=data['user'],
                          value=data['value'])
            result.save()
            return result
        except (KeyError, ValueError) as e:
            logger_models.error(f"Can not increase bid for listing data - {data}. {e}.")
            return None

    @staticmethod
    def close_listing(id: int):
        try:
            instance = Listing.objects.get(id=id)
            instance.active = False
            instance.save()
            winner = instance.get_current_bid
            result = {'best_bid': winner.value,
                      'user_winner': winner.user
                      }
            return result
        except Listing.DoesNotExist:
            logger_models.error(f"Failed to delete listing with id=({id}).")
            return None

    @staticmethod
    def listing_filter_by_category(category: str):
        """
        Return query set of active listings, filtered by category.
        :param category: Category instance
        :return: query set of Listing()
        """
        try:
            result = Listing.objects.filter(active=True, category__name=category)
            return result
        except IntegrityError as e:
            msg = f"Can not get listings by category name. {e}"
            logger_models.error(msg)
            return None


class Wishlist(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)

    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             verbose_name="User id")
    listing = models.ForeignKey(Listing,
                                related_name='wishlist',
                                on_delete=models.CASCADE,
                                verbose_name="Listing id")

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'

    @staticmethod
    def delete_from_wishlist(listing: Listing, user: User):
        try:
            instance = Wishlist.objects.get(listing=listing, user=user)
            instance.delete()
            return True
        except Wishlist.DoesNotExist:
            logger_models.error(f"Failed to delete listing ({listing})f rom user's ({user}) wishlist.")
            return None

    @staticmethod
    def add_to_wishlist(listing: Listing, user: User):
        try:
            instance = Wishlist(user=user, listing=listing)
            instance.save()
            return instance
        except Exception:
            logger_models.error(f"Failed to add listing ({listing}) to user's ({user}) wishlist.")
            return None

    @staticmethod
    def exist_in_wishlist(listing: Listing, user: User) -> bool:
        try:
            instance = Wishlist.objects.get(user=user, listing=listing)
            return True
        except Wishlist.DoesNotExist:
            return False


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

    @staticmethod
    def add_comment(listing: Listing, user: User, text):
        try:
            assert isinstance(user, User), f"User is not instance od User class"
            assert user.is_active, f"{user} user is not active user"
            assert isinstance(listing, Listing), f"listing {listing} is not instance of Listing class"
            instance = Comments(user=user,
                                listing=listing,
                                text=text)
            instance.save()
            return instance
        except (AssertionError, IntegrityError) as e:
            msg = f"Error. Can not add text ({text}) as comment to listing {listing} by user {user}. {e}."
            logger_models.error(msg)
            return None


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
