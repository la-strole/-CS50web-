# https://stackoverflow.com/questions/62100550/django-importerror-cannot-import-name-reporterprofile-from-partially-initiali
from django.forms import ModelForm
from .models import Listing


class CreateListing(ModelForm):
    class Meta:
        model = Listing
        fields = ['category', 'start_value', 'title', 'description', 'image_url']

