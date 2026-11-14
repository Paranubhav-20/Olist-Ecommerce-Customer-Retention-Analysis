
-- 1. Total delivered orders
SELECT
    COUNT(DISTINCT order_id) AS total_delivered_orders
FROM delivered_orders;


-- 2. Unique purchasing customers
SELECT
    COUNT(DISTINCT customer_unique_id) AS unique_customers
FROM delivered_orders;


-- 3. Count delivered orders per customer
SELECT
    customer_unique_id,
    COUNT(DISTINCT order_id) AS total_orders
FROM delivered_orders
GROUP BY customer_unique_id
ORDER BY total_orders DESC;


-- 4. Repeat customers and one-time customers
WITH customer_frequency AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS total_orders
    FROM delivered_orders
    GROUP BY customer_unique_id
)
SELECT
    CASE
        WHEN total_orders >= 2 THEN 'Repeat Customer'
        ELSE 'One-Time Customer'
    END AS customer_type,
    COUNT(*) AS customer_count
FROM customer_frequency
GROUP BY customer_type;


-- 5. Overall repeat customer rate
WITH customer_frequency AS (
    SELECT
        customer_unique_id,
        COUNT(DISTINCT order_id) AS total_orders
    FROM delivered_orders
    GROUP BY customer_unique_id
)
SELECT
    COUNT(*) AS total_customers,
    SUM(CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END)
        AS repeat_customers,
    ROUND(
        100.0 * SUM(
            CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS repeat_customer_rate_pct
FROM customer_frequency;


-- 6. Monthly active purchasing customers
SELECT
    strftime(
        '%Y-%m',
        order_purchase_timestamp
    ) AS purchase_month,
    COUNT(DISTINCT customer_unique_id) AS active_customers,
    COUNT(DISTINCT order_id) AS delivered_orders
FROM delivered_orders
GROUP BY purchase_month
ORDER BY purchase_month;


-- 7. Monthly repeat customer rate
WITH customer_monthly_orders AS (
    SELECT
        strftime(
            '%Y-%m',
            order_purchase_timestamp
        ) AS purchase_month,
        customer_unique_id,
        COUNT(DISTINCT order_id) AS monthly_orders
    FROM delivered_orders
    GROUP BY purchase_month, customer_unique_id
)
SELECT
    purchase_month,
    COUNT(*) AS active_customers,
    SUM(
        CASE WHEN monthly_orders >= 2 THEN 1 ELSE 0 END
    ) AS customers_with_multiple_orders_in_month,
    ROUND(
        100.0 * SUM(
            CASE WHEN monthly_orders >= 2 THEN 1 ELSE 0 END
        ) / COUNT(*),
        2
    ) AS same_month_repeat_rate_pct
FROM customer_monthly_orders
GROUP BY purchase_month
ORDER BY purchase_month;


-- 8. Monthly cohort retention

WITH customer_first_purchase AS (
    SELECT
        customer_unique_id,
        MIN(
            strftime('%Y-%m', order_purchase_timestamp)
        ) AS cohort_month
    FROM delivered_orders
    GROUP BY customer_unique_id
),

customer_activity AS (
    SELECT DISTINCT
        o.customer_unique_id,
        f.cohort_month,
        strftime(
            '%Y-%m',
            o.order_purchase_timestamp
        ) AS activity_month
    FROM delivered_orders AS o
    JOIN customer_first_purchase AS f
        ON o.customer_unique_id = f.customer_unique_id
),

cohort_activity AS (
    SELECT
        cohort_month,
        activity_month,
        COUNT(DISTINCT customer_unique_id) AS active_customers,
        (
            CAST(substr(activity_month, 1, 4) AS INTEGER)
            - CAST(substr(cohort_month, 1, 4) AS INTEGER)
        ) * 12
        + (
            CAST(substr(activity_month, 6, 2) AS INTEGER)
            - CAST(substr(cohort_month, 6, 2) AS INTEGER)
        ) AS cohort_index
    FROM customer_activity
    GROUP BY cohort_month, activity_month
),

cohort_sizes AS (
    SELECT
        cohort_month,
        active_customers AS cohort_size
    FROM cohort_activity
    WHERE cohort_index = 0
)

SELECT
    a.cohort_month,
    a.activity_month,
    a.cohort_index,
    s.cohort_size,
    a.active_customers,
    ROUND(
        100.0 * a.active_customers / s.cohort_size,
        2
    ) AS retention_pct
FROM cohort_activity AS a
JOIN cohort_sizes AS s
    ON a.cohort_month = s.cohort_month
ORDER BY a.cohort_month, a.cohort_index;

