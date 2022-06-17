from django import forms


class form_new_page(forms.Form):
    title = forms.CharField(label="Title", max_length=20)
    content = forms.CharField(widget=forms.Textarea(attrs={'label': '', 'name': 'content', 'rows': '3', 'cols': '5'}))


class form_edit_page(forms.Form):
    title = forms.CharField(label="Title", max_length=20, widget=forms.TextInput(attrs={'readonly': ''}))
    content = forms.CharField(widget=forms.Textarea(attrs={'label': '', 'name': 'content', 'rows': '3', 'cols': '5'}))


