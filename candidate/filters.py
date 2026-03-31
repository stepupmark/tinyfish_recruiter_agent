import django_filters
from recruiter.models import JobPosting
from django.db.models import Q


class JobSuggestionsFilter(django_filters.FilterSet):
    job_title = django_filters.CharFilter(lookup_expr='icontains')
    job_location = django_filters.CharFilter(lookup_expr='icontains')
    employment_type = django_filters.CharFilter(lookup_expr='iexact')
    skills_required = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.CharFilter(lookup_expr='iexact')
    search = django_filters.CharFilter(method='global_search')

    class Meta:
        model = JobPosting
        fields = [
            "job_title",
            "job_location",
            "employment_type",
            "skills_required",
            "status",
            "search",
        ]

    def global_search(self,queryset, name, value):
        return queryset.filter(
            Q(job_title__icontains=value) |
            Q(skills_required__icontains=value) |
            Q(job_location__icontains=value)
        )