-- ============================================================
-- Query 03 — Cohort Assignment
-- Goal: Assign each customer to their first purchase month
-- ============================================================

WITH first_purchase AS (
    SELECT
        c.customer_unique_id,
        MIN(CAST(o.order_purchase_timestamp AS TIMESTAMP))  AS first_order_date,
        DATE_TRUNC(
            MIN(CAST(o.order_purchase_timestamp AS TIMESTAMP)), MONTH
        )                                                   AS cohort_month
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
)

SELECT
    cohort_month,
    COUNT(DISTINCT customer_unique_id)  AS cohort_size
FROM first_purchase
GROUP BY cohort_month
ORDER BY cohort_month ASC;