"""Download Kaggle datasets, tolerating a newest version that is not yet downloadable."""

import requests
from kagglehub.clients import build_kaggle_client
from kagglesdk.datasets.types.dataset_api_service import ApiGetDatasetRequest

HTTP_NOT_FOUND = 404


def fetch_current_dataset_version(handle):
    """Return the newest version number Kaggle reports for an "owner/dataset" handle."""
    request = ApiGetDatasetRequest()
    request.owner_slug, request.dataset_slug = handle.split("/")
    with build_kaggle_client() as client:
        dataset = client.datasets.dataset_api_client.get_dataset(request)
    return dataset.current_version_number


def download_newest_available_version(
    handle, current_version, download, max_versions_to_try=5
):
    """Download the newest version of a dataset that Kaggle can actually serve.

    Kaggle sometimes marks a new version as current before its archive exists,
    so downloading it returns 404 for hours or days. Rather than failing, fall
    back to the previous versions, which are a day or so older.
    """
    oldest_version_to_try = max(current_version - max_versions_to_try + 1, 1)
    for version in range(current_version, oldest_version_to_try - 1, -1):
        try:
            return download(f"{handle}/versions/{version}")
        except requests.HTTPError as error:
            if not _is_not_found(error):
                raise
            print(f"  Version {version} of {handle} is not downloadable yet (404)")

    raise RuntimeError(
        f"No downloadable version of {handle} between "
        f"{oldest_version_to_try} and {current_version}"
    )


def _is_not_found(error):
    return error.response is not None and error.response.status_code == HTTP_NOT_FOUND
