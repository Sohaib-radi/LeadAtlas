from django import forms

from .models import Business
from .sectors import sector_choices


class SearchForm(forms.Form):
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "e.g. Morocco, France"}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={"placeholder": "e.g. Casablanca, Lyon"}))
    sector = forms.ChoiceField(label="Sector (secteur d'activité)", choices=sector_choices)
    keyword = forms.CharField(
        max_length=100,
        required=False,
        label="Name contains (optional)",
        widget=forms.TextInput(attrs={"placeholder": "e.g. pizza"}),
    )


class BusinessFilterForm(forms.Form):
    q = forms.CharField(required=False, label="Search", widget=forms.TextInput(attrs={"placeholder": "Name, address…"}))
    country = forms.CharField(required=False)
    city = forms.CharField(required=False)
    sector = forms.ChoiceField(required=False, choices=lambda: [("", "All sectors"), *sector_choices()])
    status = forms.ChoiceField(required=False, choices=[("", "All statuses"), *Business.Status.choices])
    has_phone = forms.BooleanField(required=False, label="Has phone")
    has_website = forms.BooleanField(required=False, label="Has website")
    has_email = forms.BooleanField(required=False, label="Has email")


class BusinessUpdateForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ["status", "phone", "email", "website", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 5})}
