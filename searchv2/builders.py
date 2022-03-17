from datetime import timedelta
from django.utils import timezone

from grid.models import Grid
from package.models import Package, Commit
from searchv2.models import SearchV2
from searchv2.utils import remove_prefix, clean_title


def build_1():
    now = timezone.now()
    quarter_delta = timedelta(90)
    half_year_delta = timedelta(182)
    year_delta = timedelta(365)
    last_week = now - timedelta(7)

    SearchV2.objects.filter(created__lte=last_week).delete()
    for package in Package.objects.all():
        print(f"{package}")
        obj, created = SearchV2.objects.get_or_create(
            item_type="package",
            slug=package.slug,
        )
        obj.slug_no_prefix = remove_prefix(package.slug)
        obj.clean_title = clean_title(remove_prefix(package.slug))
        obj.title = package.title
        obj.title_no_prefix = remove_prefix(package.title)
        obj.description = package.repo_description
        obj.category = package.category.title
        obj.absolute_url = package.get_absolute_url()
        obj.repo_watchers = package.repo_watchers
        obj.repo_forks = package.repo_forks
        obj.pypi_downloads = package.pypi_downloads
        obj.usage = package.usage.count()
        obj.participants = package.participants

        optional_save = False
        try:
            obj.last_committed = package.last_updated()
            optional_save = True
        except Commit.DoesNotExist:
            pass

        last_released = package.last_released()
        if last_released and last_released.upload_time:
            obj.last_released = last_released.upload_time
            optional_save = True

        if optional_save:
            obj.save()

        # Weighting part
        weight = 0
        optional_save = False

        # Read the docs!
        if package.documentation_url and len(package.documentation_url):
            weight += 20

        # rtfd_url = f"http://readthedocs.org/api/v1/build/{obj.slug}/"
        # r = requests.get(rtfd_url)
        # if r.status_code == 200:
        #     data = json.loads(r.content)
        #     if data["meta"]["total_count"]:
        #         weight += 20

        if not package.is_deprecated:

            if obj.description.strip():
                weight += 20

            if obj.repo_watchers:
                weight += min(obj.repo_watchers, 20)

            if obj.repo_forks:
                weight += min(obj.repo_forks, 20)

            if obj.pypi_downloads:
                weight += min(obj.pypi_downloads / 1000, 20)

            if obj.usage:
                weight += min(obj.usage, 20)

            # Is there ongoing work or is this forgotten?
            if obj.last_committed:
                if now - obj.last_committed < quarter_delta:
                    weight += 20
                elif now - obj.last_committed < half_year_delta:
                    weight += 10
                elif now - obj.last_committed < year_delta:
                    weight += 5

            # Is the last release less than a year old?
            last_released = obj.last_released
            if last_released:
                if now - last_released < year_delta:
                    weight += 20

            if weight:
                obj.weight = weight
                obj.save()

    max_weight = SearchV2.objects.only("weight").order_by("-weight").first().weight
    increment = max_weight / 6
    for grid in Grid.objects.all():
        obj, created = SearchV2.objects.get_or_create(
            item_type="grid",
            slug=grid.slug,
        )
        obj.slug_no_prefix = remove_prefix(grid.slug)
        obj.clean_title = clean_title(remove_prefix(grid.slug))
        obj.title = grid.title
        obj.title_no_prefix = remove_prefix(grid.title)
        obj.description = grid.description
        obj.absolute_url = grid.get_absolute_url()

        weight = max_weight - increment

        if not grid.is_locked:
            weight -= increment

        if not grid.header:
            weight -= increment

        if not grid.packages.exists():
            weight -= increment

        obj.weight = weight
        obj.save()

    return SearchV2.objects.all()
