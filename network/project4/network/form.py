from django.forms import ModelForm
from .models import Post


class New_post(ModelForm):
    class Meta:
        model = Post
        fields = ["post_text"]
