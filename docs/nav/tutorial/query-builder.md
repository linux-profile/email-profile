# Query Builder

## Shortcuts

{* ./docs_src/query_builder.py ln[10:13] *}

## Q Builder (composable)

{* ./docs_src/query_builder.py ln[15:17] *}

## OR

{* ./docs_src/query_builder.py ln[19:21] *}

## NOT

{* ./docs_src/query_builder.py ln[23:25] *}

## Date Range

{* ./docs_src/query_builder.py ln[27:29] *}

## Size Filter

{* ./docs_src/query_builder.py ln[31:33] *}

## Query (validated kwargs)

{* ./docs_src/query_builder.py ln[35:37] *}

## Exclude and OR chaining

```python
Query(subject="report").exclude(subject="spam").or_(subject="urgent")
```

## First Result

```python
msg = app.inbox.where(Query(subject="meeting")).first()
print(msg.from_)
```

## Full Code

{* ./docs_src/query_builder.py *}

## Reference

- [Query & Q](../reference/query.md)
- [Where](../reference/where.md)
- [Email](../reference/email.md)
