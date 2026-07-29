import logging
import time

import requests

from hub.dataload.sources.civic.config import CIVIC_API_KEY

MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 1.0


def post_graphql(api_url: str, payload: dict, operation_name: str):
    """POST a GraphQL query, retrying on rate-limit/server errors and
    logging the raw body when the response isn't valid JSON."""
    headers = {"Content-Type": "application/json"}
    if CIVIC_API_KEY:
        headers["Authorization"] = f"Bearer {CIVIC_API_KEY}"

    backoff = INITIAL_BACKOFF_SECONDS
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(api_url, json=payload, headers=headers)
        except requests.exceptions.RequestException as e:
            last_error = e
            logging.warning(
                f"[{operation_name}] request error (attempt {attempt}/{MAX_RETRIES}): {e}"
            )
            time.sleep(backoff)
            backoff *= 2
            continue

        if response.status_code == 429 or response.status_code >= 500:
            retry_after = response.headers.get("Retry-After")
            wait = float(retry_after) if retry_after else backoff
            logging.warning(
                f"[{operation_name}] got HTTP {response.status_code} "
                f"(attempt {attempt}/{MAX_RETRIES}), retrying in {wait}s"
            )
            last_error = requests.exceptions.HTTPError(
                f"HTTP {response.status_code}", response=response
            )
            time.sleep(wait)
            backoff *= 2
            continue

        if not response.ok:
            logging.error(
                f"[{operation_name}] request failed with HTTP {response.status_code}: "
                f"{response.text[:500]!r}"
            )
            response.raise_for_status()

        try:
            return response.json()
        except ValueError as e:
            last_error = e
            logging.warning(
                f"[{operation_name}] non-JSON response (status {response.status_code}, "
                f"attempt {attempt}/{MAX_RETRIES}): {response.text[:500]!r}"
            )
            time.sleep(backoff)
            backoff *= 2
            continue

    raise RuntimeError(
        f"[{operation_name}] failed after {MAX_RETRIES} attempts"
    ) from last_error
