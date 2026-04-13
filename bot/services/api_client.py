"""LMS API client — handles HTTP communication with the backend."""

import httpx

from config import settings


class APIClient:
    """Client for the LMS backend API.

    All methods return parsed data or raise a descriptive error string.
    """

    def __init__(self) -> None:
        self.base_url = settings.lms_api_base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.lms_api_key}",
        }

    def _build_url(self, path: str) -> str:
        """Build a full URL from a path fragment."""
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str) -> dict | list | str:
        """Make a GET request. Returns parsed JSON or an error string."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    self._build_url(path),
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            return f"connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.RequestError as e:
            return f"request failed: {e}. Check the API configuration."
        except Exception as e:
            return f"unexpected error: {e}"

    def post(self, path: str) -> dict | list | str:
        """Make a POST request. Returns parsed JSON or an error string."""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    self._build_url(path),
                    headers=self.headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError as e:
            return f"connection refused ({self.base_url}). Check that the services are running."
        except httpx.HTTPStatusError as e:
            return f"HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
        except httpx.RequestError as e:
            return f"request failed: {e}. Check the API configuration."
        except Exception as e:
            return f"unexpected error: {e}"
