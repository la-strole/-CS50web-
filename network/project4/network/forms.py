from django import forms

class NewPostForm(forms.Form):
    post_text = forms.Textarea()