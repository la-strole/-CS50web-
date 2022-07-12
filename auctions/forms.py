# https://stackoverflow.com/questions/62100550/django-importerror-cannot-import-name-reporterprofile-from-partially-initiali
from django.forms import ModelForm, Textarea
from .models import Listing, Bids, Comments, Info_msg


class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'start_value', 'title', 'description', 'image_url']
        widgets = {
            'description': Textarea(attrs={'rows': 3, 'cols': 5}, )
        }


class RaiseBid(ModelForm):
    class Meta:
        model = Bids
        fields = ['value']


class CommentsForm(ModelForm):
    class Meta:
        model = Comments
        fields = ['text']
        widgets = {
            'text': Textarea(attrs={'rows': 1, 'cols': 120}, )
        }


class CommentsFormAdmin(ModelForm):
    class Meta:
        model = Comments
        fields = ['user', 'text']
        widgets = {
            'text': Textarea(attrs={'rows': 1, 'cols': 120}, )
        }


class NotificationsFormAdmin(ModelForm):
    class Meta:
        model = Info_msg
        fields = ['title', 'text']
        widgets = {
            'title': Textarea(attrs={'rows': 1, 'cols': 60}),
            'text': Textarea(attrs={'rows': 1, 'cols': 120})
        }
