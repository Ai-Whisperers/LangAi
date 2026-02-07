# Good Python Type Hints Pattern

This minimal example demonstrates the correct application of type hints according to `rule.python.type-hints.v1`.

```python
from typing import List, Optional, Dict

class UserProcessor:
    def __init__(self, users: List[Dict[str, str]]):
        self.users = users

    def get_user_email(self, user_id: str) -> Optional[str]:
        """Retrieve user email by ID."""
        for user in self.users:
            if user.get("id") == user_id:
                return user.get("email")
        return None

    def process_all(self) -> None:
        """Process all users."""
        for user in self.users:
            self._process_single(user)

    def _process_single(self, user: Dict[str, str]) -> bool:
        """Process a single user dictionary."""
        # Processing logic...
        return True
```
