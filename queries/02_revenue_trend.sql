-- ============================================================
-- Query 02 — Monthly Revenue & Order Volume Trend
-- Goal: Understand overall business growth over time
-- Stakeholder: Head of Growth
-- ============================================================
 
SELECT
    DATE_TRUNC(CAST(o.order_purchase_timestamp AS TIMESTAMP), MONTH)   AS order_month,
    COUNT(DISTINCT o.order_id)                      AS total_orders,
    COUNT(DISTINCT c.customer_unique_id)            AS unique_customers,
    ROUND(SUM(p.payment_value), 2)                  AS total_revenue,
    ROUND(AVG(p.payment_value), 2)                  AS avg_order_value
FROM `portfolio-olist-496116.olist_raw.orders` o
JOIN `portfolio-olist-496116.olist_raw.customers` c
    USING (customer_id)
JOIN `portfolio-olist-496116.olist_raw.order_payments` p
    USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY order_month
ORDER BY order_month ASC;