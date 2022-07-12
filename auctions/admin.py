from django.contrib import admin
from . import models, forms

"""
Classes for User section.
"""


class WatchlistInstanceInline(admin.TabularInline):
    model = models.Wishlist
    extra = 0


class NotificationsInstanceInline(admin.TabularInline):
    model = models.Info_msg
    extra = 0
    readonly_fields = ('timestamp',)
    form = forms.NotificationsFormAdmin


class UserAdmin(admin.ModelAdmin):
    inlines = [WatchlistInstanceInline, NotificationsInstanceInline]


"""
Classes for Listing section.
"""


class CommentsInstanceInline(admin.TabularInline):
    model = models.Comments
    extra = 0
    readonly_fields = ('timestamp',)
    form = forms.CommentsFormAdmin


class BidsInstanceInline(admin.TabularInline):
    model = models.Bids
    extra = 0
    readonly_fields = ('timestamp',)


class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'category', 'start_value', 'get_current_bid', 'comments_count', 'active',
                    'timestamp']
    fieldsets = (
        (None, {'fields': ['title', 'user', 'category', 'start_value']}),
        ('Detailed', {'fields': ['description', 'image_url']})
                )
    list_filter = ('active', 'category', 'user')
    inlines = [CommentsInstanceInline, BidsInstanceInline]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Category)
admin.site.register(models.Listing, ListingAdmin)
