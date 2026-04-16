# Retry Decorator

Use the built-in retry with exponential backoff for your own functions.

```python
from email_profile.advanced import with_retry

@with_retry(attempts=5, base_delay=1.0)
def flaky_operation():
    ...
```

Automatically retries on transient errors. Backs off exponentially between attempts. Does not retry on `QuotaExceeded`.

## Reference

- [Errors](../reference/errors.md)
