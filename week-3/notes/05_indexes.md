# 05 — Indexes

## What it is

An **index** is a data structure (usually a B-tree) that lets the database find rows quickly without scanning every row in the table. Like an index in a book — instead of reading every page, you look up the topic and jump directly there.

## Why it matters

Indexes are the first tool for query performance tuning. In interviews, you'll be asked when to add them, when they hurt (write-heavy tables), and how to verify they're being used.

## The code

```sql
-- Create index on frequently filtered column
CREATE INDEX idx_orders_status ON orders(status);

-- Check if index is used
EXPLAIN QUERY PLAN
SELECT * FROM orders WHERE status = 'delivered';
```

## Sample output

**Before index:**
```
SCAN orders
```

**After index:**
```
SEARCH orders USING INDEX idx_orders_status (status=?)
```

`SEARCH` with `USING INDEX` means the index is being used. `SCAN` means full table scan.

## Common interview questions

1. **When should you NOT add an index?** Small tables, columns with low cardinality (e.g. boolean), write-heavy tables where index maintenance slows inserts.
2. **Composite index column order?** Leftmost prefix rule: index on `(a, b)` helps `WHERE a = ?` and `WHERE a = ? AND b = ?` but not `WHERE b = ?` alone.
3. **Index vs partitioning?** Indexes speed up lookups within a table; partitioning splits the table itself for manageability and pruning.
