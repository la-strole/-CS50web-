from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    id = models.AutoField(editable=False,
                          primary_key=True)
    id.db_index()

    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)


class User_groups(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)
    id.db_index()

    class UserGroupsNames(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        WATCHER = 'Watcher', 'Watcher'
        PARTICIPANT = 'Participant', 'Participant'
        CREATOR = 'Creator', 'Creator'
        MODERATOR = 'Moderator', 'Moderator'

    group_name = models.CharField("User group name",
                                  max_length=16,
                                  help_text="User group name (max 16 characters)",
                                  choices=UserGroupsNames.choices,
                                  unique=True,
                                  default=UserGroupsNames.WATCHER)

    class Meta:
        db_table = 'user_groups'
        verbose_name = 'User Groups'
        verbose_name_plural = 'User Groups'

    def __str__(self):
        return f'{self.group_name}'


class User_roles(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)
    id.db_index()

    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE)
    group_id = models.ForeignKey(User_groups,
                                 on_delete=models.CASCADE,
                                 related_name='users')

    class Meta:
        db_table = 'user_roles'


class Category(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)
    id.db_index()

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
    id.db_index()

    active = models.BooleanField(default=True, editable=False)
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name="User id")
    category_id = models.ForeignKey(Category,
                                    on_delete=models.SET_DEFAULT,
                                    verbose_name="Category id")
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
        return f'{self.title} from {self.user_id}'


class Wishlist(models.Model):
    id = models.AutoField(editable=False,
                          primary_key=True)
    id.db_index()

    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name="User id")
    listing_id = models.ForeignKey(Listing,
                                   on_delete=models.CASCADE,
                                   verbose_name="Listing id")

    class Meta:
        db_table = 'wishlist'
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'


class Comments(models.Model):
    id = models.BigAutoField(editable=False, primary_key=True)
    id.db_index()

    user_id = models.ForeignKey(User,
                                on_delete=models.SET('Deleted user'),
                                verbose_name="User id")
    listing_id = models.ForeignKey(Listing,
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
    id.db_index()

    listing_id = models.ForeignKey(Listing,
                                   on_delete=models.CASCADE,
                                   verbose_name="Listing id")
    user_id = models.ForeignKey(User,
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
    id.db_index()

    is_read = models.BooleanField(default=False, editable=False)
    user_id = models.ForeignKey(User,
                                on_delete=models.CASCADE,
                                verbose_name="User id")
    text = models.TextField(max_length=120, editable=False)
    timestamp = models.DateTimeField(editable=False,
                                     auto_now=True)

    class Meta:
        db_table = 'info_msg'
        verbose_name = 'Information message'
        verbose_name_plural = 'Information messages'
