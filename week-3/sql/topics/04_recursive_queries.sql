-- Topic 04: Recursive Queries (employee-manager hierarchy)
-- Database: retail_oltp.db

WITH RECURSIVE org_chart AS (
    -- Anchor: top-level employees (no manager)
    SELECT
        employee_id,
        first_name || ' ' || last_name AS name,
        title,
        manager_id,
        0 AS depth,
        first_name || ' ' || last_name AS path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: employees reporting to someone already in the tree
    SELECT
        e.employee_id,
        e.first_name || ' ' || e.last_name,
        e.title,
        e.manager_id,
        oc.depth + 1,
        oc.path || ' > ' || e.first_name || ' ' || e.last_name
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.employee_id
    WHERE oc.depth < 5  -- safety limit
)
SELECT employee_id, name, title, depth, path
FROM org_chart
ORDER BY path
LIMIT 20;
