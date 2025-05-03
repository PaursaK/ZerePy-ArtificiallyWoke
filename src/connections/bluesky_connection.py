import logging
from typing import Dict, Any
from src.actions import bluesky_actions
import datetime
from src.connections.base_connection import BaseConnection, Action, ActionParameter

logger = logging.getLogger("connections.bluesky_connection")

class BlueskyConnectionError(Exception):
    """Base exception for Bluesky connection errors"""
    pass

class BlueskyConfigurationError(BlueskyConnectionError):
    """Raised when there are configuration/credential issues"""
    pass

class BlueskyAPIError(BlueskyConnectionError):
    """Raised when Bluesky API requests fail"""
    pass

class BlueskyConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._client = None  # Placeholder for API client or session

    ### ADDED THIS FUNCTION TO CHECK IF THE CONNECTION IS CONFIGURED  ###
    def is_configured(self, verbose: bool = False) -> bool:
            """Check if the Bluesky connection is configured"""
            try:
                # For simplicity, consider it configured if access token is present
                return hasattr(self, "_access_jwt") and self._access_jwt is not None
            except Exception as e:
                if verbose:
                    logger.error(f"Error checking Bluesky configuration: {e}")
                return False

    @property
    def is_llm_provider(self) -> bool:
        # Bluesky is a social platform, not an LLM provider
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Bluesky configuration from JSON"""
        required_fields = ["api_key", "api_secret", "access_token", "access_token_secret"]
        missing_fields = [field for field in required_fields if field not in config]

        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")

        # Additional validation can be added here
        return config

    def register_actions(self) -> None:
        """Register available Bluesky actions"""
        self.actions = {
            "post-bluesky": Action(
                name="post-bluesky",
                parameters=[
                    ActionParameter("text", True, str, "Text content of the post")
                ],
                description="Create a new post on Bluesky"
            )
        }

    def configure(self) -> bool:
        """Configure the Bluesky API client/session"""
        import requests
        import time

        logger.info("Configuring Bluesky connection...")

        # Required config keys
        username: str = self.config.get("username")
        password: str = self.config.get("password")
        pds_host: str = self.config.get("pds_host", "https://bsky.social")

        if not username or not password:
            raise BlueskyConfigurationError("Username and password must be provided in config")

        # Create session to get access and refresh tokens
        session_url: str = f"{pds_host}/xrpc/com.atproto.server.createSession"
        payload: Dict[str, str] = {
            "identifier": username,
            "password": password
        }

        try:
            response = requests.post(session_url, json=payload)
            response.raise_for_status()
            data: Dict[str, Any] = response.json()
            self._access_jwt = data.get("accessJwt")
            self._refresh_jwt = data.get("refreshJwt")
            self._token_expiry = time.time() + 300  # Access token expires in ~5 minutes
            logger.info("Bluesky authentication successful")
            return True
        except Exception as e:
            logger.error(f"Failed to authenticate with Bluesky: {e}")
            return False

    def perform_action(self, action_name: str, params: Any = None) -> Any:
        """Perform an action on Bluesky platform"""
        import requests
        import datetime

        if not hasattr(self, "_access_jwt") or not self._access_jwt:
            raise BlueskyAPIError("Not authenticated. Call configure() first.")

        # Refresh token if expired (simple check)
        import time
        if time.time() > getattr(self, "_token_expiry", 0):
            logger.info("Access token expired, refreshing not implemented yet")
            # Implement refresh logic here if needed

        headers = {
            "Authorization": f"Bearer {self._access_jwt}",
            "Content-Type": "application/json"
        }

        pds_host = self.config.get("pds_host", "https://bsky.social")

        if action_name == "post" or action_name == "post-bluesky":
            text = params.get("text") if params else None
            if not text:
                raise BlueskyAPIError("Missing 'text' parameter for post action")

            post_url = f"{pds_host}/xrpc/com.atproto.repo.createRecord"
            post_data = {
                "repo": self.config.get("username"),
                "collection": "app.bsky.feed.post",
                "record": {
                    "$type": "app.bsky.feed.post",
                    "text": text,
                    "createdAt": datetime.datetime.utcnow().isoformat() + "Z"
                }
            }

            try:
                response = requests.post(post_url, headers=headers, json=post_data)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                try:
                    error_content = e.response.text if hasattr(e, 'response') else str(e)
                except Exception:
                    error_content = str(e)
                logger.error(f"Failed to create post: {error_content}")
                raise BlueskyAPIError(f"Post creation failed: {error_content}")

        else:
            logger.error(f"Unknown action '{action_name}'")
            raise BlueskyAPIError(f"Unknown action '{action_name}'")