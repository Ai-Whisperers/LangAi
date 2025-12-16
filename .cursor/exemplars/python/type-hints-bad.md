# Bad Python Type Hints Pattern

This example uses `critic-only` mode to demonstrate what NOT to do. Violates `rule.python.type-hints.v1`.

```python
class UserProcessor:
    # Missing type hints for parameter
    def __init__(self, users):
        self.users = users

    # Missing return type annotation
    # Missing parameter type hint
    def get_user_email(self, user_id):
        """Retrieve user email by ID."""
        for user in self.users:
            if user.get("id") == user_id:
                return user.get("email")
        return None

    # Missing return type (should be -> None)
    def process_all(self):
        """Process all users."""
        for user in self.users:
            self._process_single(user)

    # Using Any implicitly
    def _process_single(self, user):
        """Process a single user dictionary."""
        # Processing logic...
        return True
```
