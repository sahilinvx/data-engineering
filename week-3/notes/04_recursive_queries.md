# 04 — Recursive Queries

## What it is

A **recursive query** uses a CTE that references itself to walk hierarchical data — org charts, bill of materials, category trees, folder structures. It has two parts: an **anchor** (starting rows) and a **recursive** part (find children of rows already found).

## Why it matters

Hierarchy traversal comes up in employee reporting lines, product category trees, and graph-like data. Recursive CTEs are the SQL-native solution (vs writing a loop in Python).

## The code

```sql
WITH RECURSIVE org_chart AS (
    -- Anchor: top-level (no manager)
    SELECT employee_id, name, manager_id, 0 AS depth, name AS path
    FROM employees WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: find reports of people already in the tree
    SELECT e.employee_id, e.name, e.manager_id, oc.depth + 1,
           oc.path || ' > ' || e.name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart ORDER BY path;
```

## Sample output

```
CEO Name | CEO | 0 | CEO Name
CEO Name > Manager A | Manager A | 1 | CEO Name > Manager A
CEO Name > Manager A > Associate B | Associate B | 2 | ...
```

## Common interview questions

1. **When do you need UNION ALL vs UNION?** Always `UNION ALL` in recursive CTEs — `UNION` deduplicates and breaks recursion.
2. **How do you prevent infinite loops?** Add a depth limit (`WHERE depth < 10`) or cycle detection.
3. **Recursive CTE vs self-join?** Self-join handles fixed depth (1 or 2 levels); recursive handles arbitrary depth.
