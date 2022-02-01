#!/usr/bin/env python
"""
This script fetches a list of published ap-airflow images, filters out images
that have been obsoleted by higher patch-levels, filters out images past their
end-of-life date, and then outputs a list of image tags suitable for mirroring

It uses end-of-life data from enterprise_support_data.json and a live list of
published images from api sources. It also sanity-checks tags to make sure they
exist in the public quay repo so that we know they can be mirrored.
"""
import json
import yaml
import urllib.request
import semver
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from os import environ

airflow_releases_url = "https://updates.astronomer.io/astronomer-certified"
airflow_images_tags_url = "https://quay.io/v1/repositories/astronomer/ap-airflow/tags"

# see https://docs.astronomer.io/enterprise/ac-support-policy/#end-of-maintenance-date
with open("enterprise_support_data.json") as f:
    enterprise_support_data = json.load(f)
published_eol_dates = enterprise_support_data["astronomer_airflow_published_eol_dates"]

# takes release as an argument
def semver_of(release):
    return semver.VersionInfo.parse(release["version"])


# takes semvers as arguments
def is_same_patch_version(a, b):
    return (a.major == b.major) and (a.minor == b.minor) and (a.patch == b.patch)


# takes semvers as arguments
def is_same_minor_version(a, b):
    return (a.major == b.major) and (a.minor == b.minor)


# takes releases as an arguments
def obsoletes(release_a, release_b):
    a = semver_of(release_a)
    b = semver_of(release_b)
    if is_same_minor_version(a, b) and a > b:
        return True


# whether or not a release is in-support
def in_support(release):
    sv = semver_of(release)
    release_date = datetime.fromisoformat(release["release_date"])
    half_year_minimum = release_date + relativedelta(days=180)
    published_eol = next(
        (
            datetime.fromisoformat(eol_release_data["published_eol"])
            for eol_release_data in published_eol_dates
            if sv.major == eol_release_data["major"]
            and sv.minor == eol_release_data["minor"]
        ),
        False,
    )

    if not published_eol or published_eol < half_year_minimum:
        eol = half_year_minimum
    else:
        eol = published_eol

    right_now = datetime.now(timezone.utc)
    if right_now < eol:
        return True


def get_supported_airflow_image_tags():
    with urllib.request.urlopen(airflow_releases_url) as f:
        releases_raw_yaml = f.read().decode("utf-8")
    releases_doc = yaml.safe_load(releases_raw_yaml)
    available_releases = releases_doc["available_releases"]
    # ap-airflow is not versioned with semver - it is a semverlike
    # and (mis-)uses the prerelease field for build version. images without
    # prerelease fields are floating image tags and we are only interested
    # in our immutably tagged images

    immutable_releases = [
        release
        for release in available_releases
        if semver_of(release).prerelease is not None
    ]

    # find all releases without any higher build-levels to define the start of their support window
    initial_releases = []
    for release in immutable_releases:
        worse_build = next(
            (
                another_release
                for another_release in immutable_releases
                if obsoletes(release, another_release)
            ),
            False,
        )
        if not worse_build:
            initial_releases.append(release)

    # we should publish an enterprise specific variant of airflow_releases_url
    # with our start and end of support releases
    initial_release_versions_still_under_support = [
        release for release in initial_releases if in_support(release)
    ]

    most_recent_releases = []
    for release in immutable_releases:
        better_build = next(
            (
                another_release
                for another_release in immutable_releases
                if obsoletes(another_release, release)
            ),
            False,
        )
        if not better_build:
            most_recent_releases.append(release)

    supported_current_releases = [
        release
        for release in most_recent_releases
        for initial_release in initial_release_versions_still_under_support
        if is_same_minor_version(semver_of(release), semver_of(initial_release))
    ]

    # flatten the various tags under releases into a list
    supported_current_tags = [
        tag
        for release_tags in (release["tags"] for release in supported_current_releases)
        for tag in release_tags
    ]

    #### sanity check - pull the registry and make sure they all actually exist
    # returned values are in the form of tag => hash and we just want the tags
    with urllib.request.urlopen(airflow_images_tags_url) as f:
        images_raw_yaml = f.read().decode("utf-8")
    images_doc = yaml.safe_load(images_raw_yaml)
    image_tags_on_registry = images_doc.keys()
    for tag in supported_current_tags:
        assert tag in image_tags_on_registry
    ### now that we are sure that all values exist in the registry...
    return supported_current_tags


supported_current_tags = get_supported_airflow_image_tags()
image_names = [f"quay.io/astronomer/ap-airflow:{tag}" for tag in supported_current_tags]
for image_name in image_names:
    print(image_name)
