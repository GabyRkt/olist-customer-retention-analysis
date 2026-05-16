-- ============================================================
-- Query 07 — Review Score vs Retention
-- Goal: Do customers who left bad reviews churn faster?
-- Multi-table join: orders + customers + reviews + cohort logic
-- Stakeholder: Head of Growth
-- ============================================================

WITH first_purchase AS (
    -- Assign each customer to their cohort
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

customer_reviews AS (
    -- Get average review score per customer
    SELECT
        c.customer_unique_id,
        ROUND(AVG(r.review_score), 2)       AS avg_review_score,
        COUNT(DISTINCT r.review_id)         AS nb_reviews
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    JOIN `portfolio-olist-496116.olist_raw.order_reviews` r
        USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

returning_customers AS (
    -- Customers who ordered more than once
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
    -- Segment by review score
    CASE
        WHEN cr.avg_review_score >= 4 THEN '4-5 Positive'
        WHEN cr.avg_review_score >= 3 THEN '3 Neutral'
        ELSE '1-2 Negative'
    END                                                         AS review_segment,
    COUNT(DISTINCT fp.customer_unique_id)                       AS total_customers,
    COUNT(DISTINCT rc.customer_unique_id)                       AS returning_customers,
    ROUND(
        COUNT(DISTINCT rc.customer_unique_id) * 100.0
        / COUNT(DISTINCT fp.customer_unique_id)
    , 2)                                                        AS retention_rate,
    ROUND(AVG(cr.avg_review_score), 2)                         AS avg_score
FROM first_purchase fp
LEFT JOIN customer_reviews cr
    USING (customer_unique_id)
LEFT JOIN returning_customers rc
    USING (customer_unique_id)
WHERE fp.cohort_month >= '2017-01-01'
GROUP BY review_segment
ORDER BY avg_score DESC;