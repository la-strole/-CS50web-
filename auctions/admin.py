from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.User_roles)
admin.site.register(models.User)
admin.site.register(models.User_groups_names)
admin.site.register(models.Bids)
admin.site.register(models.Category)
admin.site.register(models.Comments)
admin.site.register(models.Info_msg)
admin.site.register(models.Listing)
admin.site.register(models.Wishlist)

