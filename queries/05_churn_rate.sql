-- ============================================================
-- Query 05 — Churn Rate by Cohort
-- Goal: What % of each cohort never came back after month 0?
-- Stakeholder: Head of Growth
-- ============================================================

WITH first_purchase AS (
    -- Assign each customer to their cohort (first purchase month)
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

returning_customers AS (
    -- Find customers who ordered more than once
    SELECT
        c.customer_unique_id
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
    HAVING COUNT(DISTINCT o.order_id) > 1
)

SELECT
    fp.cohort_month,
    COUNT(DISTINCT fp.customer_unique_id)                           AS cohort_size,
    COUNT(DISTINCT rc.customer_unique_id)                           AS returning_customers,
    COUNT(DISTINCT fp.customer_unique_id) 
        - COUNT(DISTINCT rc.customer_unique_id)                     AS churned_customers,
    ROUND(
        (COUNT(DISTINCT fp.customer_unique_id) 
        - COUNT(DISTINCT rc.customer_unique_id)) * 100.0 
        / COUNT(DISTINCT fp.customer_unique_id)
    , 2)                                                            AS churn_rate,
    ROUND(
        COUNT(DISTINCT rc.customer_unique_id) * 100.0 
        / COUNT(DISTINCT fp.customer_unique_id)
    , 2)                                                            AS retention_rate
FROM first_purchase fp
LEFT JOIN returning_customers rc
    USING (customer_unique_id)
WHERE fp.cohort_month >= '2017-01-01'
GROUP BY fp.cohort_month
ORDER BY fp.cohort_month;
