from django.db import models
from django.urls import reverse

from .sectors import sector_label


class Search(models.Model):
    """One business search (country + city + sector)."""

    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    sector = models.CharField(max_length=50)
    keyword = models.CharField(max_length=100, blank=True, help_text="Optional name filter")
    result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "searches"

    def __str__(self):
        return f"{self.sector_label} in {self.city}, {self.country}"

    @property
    def sector_label(self):
        return sector_label(self.sector)

    def get_absolute_url(self):
        return reverse("leads:search_detail", args=[self.pk])


class Business(models.Model):
    """A business (lead) found through a search."""

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        INTERESTED = "interested", "Interested"
        CLIENT = "client", "Client"
        NOT_INTERESTED = "not_interested", "Not interested"

    source = models.CharField(max_length=20, default="osm")
    external_id = models.CharField(max_length=50, unique=True, help_text="e.g. node/123456 for OpenStreetMap")

    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=50, db_index=True)
    category = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    address = models.CharField(max_length=255, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=255, blank=True)
    website = models.URLField(max_length=500, blank=True)
    opening_hours = models.CharField(max_length=255, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    notes = models.TextField(blank=True)
    searches = models.ManyToManyField(Search, related_name="businesses", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "businesses"

    def __str__(self):
        return self.name

    @property
    def sector_label(self):
        return sector_label(self.sector)

    @property
    def map_url(self):
        if self.latitude is None or self.longitude is None:
            return ""
        return f"https://www.openstreetmap.org/?mlat={self.latitude}&mlon={self.longitude}#map=18/{self.latitude}/{self.longitude}"

    def get_absolute_url(self):
        return reverse("leads:business_detail", args=[self.pk])
