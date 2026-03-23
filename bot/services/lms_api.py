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

    def get_items(self) -> list[dict[str, Any]]:
        """
        Get all items (labs and tasks) from the backend.

        Returns:
            List of all items with 'name', 'title', 'type' fields
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_learners(self) -> list[dict[str, Any]]:
        """
        Get all enrolled learners.

        Returns:
            List of learner records with id, name, group fields
        """
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict[str, Any]]:
        """
        Get score distribution (4 buckets) for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of score bucket records with ranges and counts
        """
        response = self._client.get(
            "/analytics/scores",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

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

    def get_timeline(self, lab: str) -> list[dict[str, Any]]:
        """
        Get submission timeline (submissions per day) for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of timeline records with dates and submission counts
        """
        response = self._client.get(
            "/analytics/timeline",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict[str, Any]]:
        """
        Get per-group scores and student counts for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            List of group records with group name, average score, student count
        """
        response = self._client.get(
            "/analytics/groups",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 5) -> list[dict[str, Any]]:
        """
        Get top N learners by score for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")
            limit: Number of top learners to return (default: 5)

        Returns:
            List of top learner records with name, score, rank
        """
        response = self._client.get(
            "/analytics/top-learners",
            params={"lab": lab, "limit": limit},
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict[str, Any]:
        """
        Get completion rate percentage for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04")

        Returns:
            Dict with completion_rate percentage
        """
        response = self._client.get(
            "/analytics/completion-rate",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict[str, Any]:
        """
        Trigger a data sync from the autochecker.

        Returns:
            Dict with sync status message
        """
        response = self._client.post("/pipeline/sync")
        response.raise_for_status()
        return response.json()

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


def create_lms_client(base_url: str, api_key: str) -> LMSAPIClient:
    """Factory function to create an LMS API client."""
    return LMSAPIClient(base_url, api_key)
