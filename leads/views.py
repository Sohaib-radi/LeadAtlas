import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BusinessFilterForm, BusinessUpdateForm, SearchForm
from .models import Business, Search
from .services import SearchError, run_search

CSV_FIELDS = [
    "name", "sector_label", "category", "country", "city", "address", "postcode",
    "phone", "email", "website", "opening_hours", "latitude", "longitude", "status", "notes", "map_url",
]


def home(request):
    form = SearchForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            search = run_search(**form.cleaned_data)
        except SearchError as exc:
            messages.error(request, str(exc))
        else:
            messages.success(request, f"Found {search.result_count} businesses.")
            return redirect(search)
    context = {
        "form": form,
        "recent_searches": Search.objects.all()[:8],
        "stats": {
            "businesses": Business.objects.count(),
            "searches": Search.objects.count(),
            "cities": Business.objects.values("city").distinct().count(),
            "with_phone": Business.objects.exclude(phone="").count(),
        },
    }
    return render(request, "leads/home.html", context)


def _filtered_businesses(params, queryset=None):
    queryset = Business.objects.all() if queryset is None else queryset
    form = BusinessFilterForm(params)
    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            queryset = queryset.filter(
                Q(name__icontains=data["q"]) | Q(address__icontains=data["q"]) | Q(category__icontains=data["q"])
            )
        if data["country"]:
            queryset = queryset.filter(country__icontains=data["country"])
        if data["city"]:
            queryset = queryset.filter(city__icontains=data["city"])
        if data["sector"]:
            queryset = queryset.filter(sector=data["sector"])
        if data["status"]:
            queryset = queryset.filter(status=data["status"])
        if data["has_phone"]:
            queryset = queryset.exclude(phone="")
        if data["has_website"]:
            queryset = queryset.exclude(website="")
        if data["has_email"]:
            queryset = queryset.exclude(email="")
    return form, queryset


def business_list(request):
    form, queryset = _filtered_businesses(request.GET)
    page = Paginator(queryset, 50).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(
        request,
        "leads/business_list.html",
        {"form": form, "page": page, "total": queryset.count(), "querystring": query.urlencode()},
    )


def search_detail(request, pk):
    search = get_object_or_404(Search, pk=pk)
    form, queryset = _filtered_businesses(request.GET, search.businesses.all())
    page = Paginator(queryset, 50).get_page(request.GET.get("page"))
    query = request.GET.copy()
    query.pop("page", None)
    return render(
        request,
        "leads/search_detail.html",
        {"search": search, "form": form, "page": page, "total": queryset.count(), "querystring": query.urlencode()},
    )


def search_list(request):
    searches = Search.objects.annotate(saved=Count("businesses"))
    page = Paginator(searches, 50).get_page(request.GET.get("page"))
    return render(request, "leads/search_list.html", {"page": page})


def search_rerun(request, pk):
    search = get_object_or_404(Search, pk=pk)
    if request.method != "POST":
        return redirect(search)
    try:
        new_search = run_search(search.country, search.city, search.sector, search.keyword)
    except SearchError as exc:
        messages.error(request, str(exc))
        return redirect(search)
    messages.success(request, f"Refreshed: {new_search.result_count} businesses.")
    return redirect(new_search)


def business_detail(request, pk):
    business = get_object_or_404(Business, pk=pk)
    form = BusinessUpdateForm(request.POST or None, instance=business)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Lead updated.")
        return redirect(business)
    return render(request, "leads/business_detail.html", {"business": business, "form": form})


def export_csv(request):
    queryset = Business.objects.all()
    filename = "leadatlas-leads.csv"
    if search_id := request.GET.get("search"):
        search = get_object_or_404(Search, pk=search_id)
        queryset = search.businesses.all()
        filename = f"leadatlas-{search.city}-{search.sector}.csv".replace(" ", "_").lower()
    _, queryset = _filtered_businesses(request.GET, queryset)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write("﻿")  # BOM so Excel opens accents correctly
    writer = csv.writer(response)
    writer.writerow(CSV_FIELDS)
    for business in queryset.iterator():
        writer.writerow([getattr(business, field) or "" for field in CSV_FIELDS])
    return response
