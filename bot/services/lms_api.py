"""
LMS API client service.

Handles all communication with the LMS backend.
Uses Bearer token authentication.
"""

import httpx
from typing import Any


class LMSAPIClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def health_check(self) -> dict[str, Any]:
        """
        Check if backend is healthy.
        
        Returns:
            dict with 'healthy' bool and 'item_count' int
            
        Raises:
            httpx.RequestError: if backend is unreachable
            httpx.HTTPStatusError: if backend returns error status
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        items = response.json()
        return {"healthy": True, "item_count": len(items)}

    def get_labs(self) -> list[dict[str, Any]]:
        """
        Get all labs from the backend.
        
        Returns:
            List of lab items with 'name', 'title', 'type' fields
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        items = response.json()
        # Filter for labs (type contains "lab")
        return [item for item in items if item.get("type", "").lower().startswith("lab")]

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """
        Get per-task pass rates for a specific lab.
        
        Args:
            lab: Lab identifier (e.g., "lab-04")
            
        Returns:
            List of pass rate records with task names and percentages
        """
        response = self._client.get(
            "/analytics/pass-rates",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()


def create_lms_client(base_url: str, api_key: str) -> LMSAPIClient:
    """Factory function to create an LMS API client."""
    return LMSAPIClient(base_url, api_key)
