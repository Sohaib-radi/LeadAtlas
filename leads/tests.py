from unittest import mock

from django.test import TestCase
from django.urls import reverse

from .models import Business, Search
from .services import SearchError, build_overpass_query, run_search

PLACE = {"osm_type": "relation", "osm_id": "123", "boundingbox": ["1", "2", "3", "4"]}
ELEMENTS = [
    {"type": "node", "id": 1, "lat": 34.0, "lon": -6.8,
     "tags": {"name": "Café Atlas", "amenity": "cafe", "phone": "+212 1;+212 2", "website": "atlas.ma",
              "addr:street": "Rue A", "addr:housenumber": "5"}},
    {"type": "way", "id": 2, "center": {"lat": 34.1, "lon": -6.9}, "tags": {"name": "Café Rif", "amenity": "cafe"}},
    {"type": "node", "id": 3, "tags": {"amenity": "cafe"}},  # unnamed: skipped
]


class QueryTests(TestCase):
    def test_area_query(self):
        query = build_overpass_query(PLACE, "bar", keyword='o"k')
        self.assertIn("area(id:3600000123)", query)
        self.assertIn('nwr["amenity"="pub"]["name"]', query)
        self.assertIn('["name"~"o\\"k",i]', query)

    def test_bbox_query_and_wildcard_tag(self):
        query = build_overpass_query({"osm_type": "node", "boundingbox": ["1", "2", "3", "4"]}, "all_shops")
        self.assertIn('nwr["shop"]["name"](1.0,3.0,2.0,4.0);', query)

    def test_unknown_sector(self):
        with self.assertRaises(SearchError):
            build_overpass_query(PLACE, "nope")


@mock.patch("leads.services.fetch_places", return_value=ELEMENTS)
@mock.patch("leads.services.geocode", return_value=PLACE)
class RunSearchTests(TestCase):
    def test_stores_businesses(self, *_):
        search = run_search("Morocco", "Rabat", "cafe")
        self.assertEqual(search.result_count, 2)
        atlas = Business.objects.get(external_id="node/1")
        self.assertEqual(atlas.phone, "+212 1")
        self.assertEqual(atlas.website, "https://atlas.ma")
        self.assertEqual(atlas.address, "5 Rue A")
        self.assertEqual(Business.objects.get(external_id="way/2").latitude, 34.1)

    def test_rerun_keeps_status_and_dedupes(self, *_):
        run_search("Morocco", "Rabat", "cafe")
        Business.objects.filter(external_id="node/1").update(status="client")
        run_search("Morocco", "Rabat", "cafe")
        self.assertEqual(Business.objects.count(), 2)
        self.assertEqual(Business.objects.get(external_id="node/1").status, "client")

    def test_views(self, *_):
        response = self.client.post(reverse("leads:home"), {"country": "Morocco", "city": "Rabat", "sector": "cafe"})
        search = Search.objects.get()
        self.assertRedirects(response, search.get_absolute_url())
        self.assertContains(self.client.get(search.get_absolute_url()), "Café Atlas")
        self.assertContains(self.client.get(reverse("leads:business_list"), {"has_phone": "on"}), "Café Atlas")
        self.assertNotContains(self.client.get(reverse("leads:business_list"), {"has_phone": "on"}), "Café Rif")
        self.assertContains(self.client.get(reverse("leads:search_list")), "Rabat")
        csv = self.client.get(reverse("leads:export_csv"), {"search": search.pk}).content.decode()
        self.assertIn("Café Atlas", csv)
        business = Business.objects.get(external_id="node/1")
        self.client.post(business.get_absolute_url(), {"status": "contacted", "phone": "1", "email": "", "website": "", "notes": "x"})
        business.refresh_from_db()
        self.assertEqual(business.status, "contacted")


class ErrorTests(TestCase):
    @mock.patch("leads.services.geocode", side_effect=SearchError("Location not found"))
    def test_error_message(self, _):
        response = self.client.post(reverse("leads:home"), {"country": "X", "city": "Y", "sector": "cafe"}, follow=True)
        self.assertContains(response, "Location not found")
        self.assertEqual(Search.objects.count(), 0)
