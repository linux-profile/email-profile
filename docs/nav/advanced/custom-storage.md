# Custom Storage Backend

Implement `StorageABC` to use your own persistence layer (PostgreSQL, Redis, S3, etc).

```python
from email_profile.advanced import StorageABC
from email_profile.serializers.raw import RawSerializer


class RedisStorage(StorageABC):

    def save(self, raw: RawSerializer) -> bool:
        ...

    def get(self, message_id: str):
        ...

    def ids(self, mailbox=None) -> set[str]:
        ...

    def uids(self, mailbox: str) -> set[str]:
        ...
```

Then use it with the `Email` class:

```python
from email_profile import Email

storage = RedisStorage()
with Email.from_env(storage=storage) as app:
    app.sync()
```
