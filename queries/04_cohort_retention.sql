-- ============================================================
-- Query 04 — Monthly Cohort Retention Matrix
-- Goal: For each cohort, track how many customers came back in months 1, 2, 3... after their first purchase
-- Stakeholder: Head of Growth
-- ============================================================

WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC(
            MIN(CAST(CAST(o.order_purchase_timestamp AS TIMESTAMP) AS DATE)), MONTH
        ) AS cohort_month
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

all_orders AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC(
            CAST(CAST(o.order_purchase_timestamp AS TIMESTAMP) AS DATE), MONTH
        ) AS order_month
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    WHERE o.order_status = 'delivered'
),

cohort_orders AS (
    SELECT
        fp.cohort_month,
        fp.customer_unique_id,
        DATE_DIFF(ao.order_month, fp.cohort_month, MONTH) AS month_number
    FROM first_purchase fp
    JOIN all_orders ao
        USING (customer_unique_id)
),

cohort_sizes AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_unique_id) AS cohort_size
    FROM first_purchase
    GROUP BY cohort_month
)

SELECT
    co.cohort_month,
    cs.cohort_size,
    co.month_number,
    COUNT(DISTINCT co.customer_unique_id)                    AS retained_customers,
    ROUND(
        COUNT(DISTINCT co.customer_unique_id) * 100.0 / cs.cohort_size
    , 2)                                                     AS retention_rate
FROM cohort_orders co
JOIN cohort_sizes cs
    USING (cohort_month)
WHERE co.cohort_month >= '2017-01-01'
  AND co.month_number >= 0
GROUP BY co.cohort_month, cs.cohort_size, co.month_number
ORDER BY co.cohort_month, co.month_number;