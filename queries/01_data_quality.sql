-- ============================================================
-- Query 01 — Data Quality Check
-- Goal: Understand the dataset before any analysis
-- ============================================================

-- 1. Row counts per table
SELECT 'customers'   AS table_name, COUNT(*) AS row_count FROM `portfolio-olist-496116.olist_raw.customers`
UNION ALL
SELECT 'orders',                     COUNT(*) FROM `portfolio-olist-496116.olist_raw.orders`
UNION ALL
SELECT 'order_items',                COUNT(*) FROM `portfolio-olist-496116.olist_raw.order_items`
UNION ALL
SELECT 'order_payments',             COUNT(*) FROM `portfolio-olist-496116.olist_raw.order_payments`
UNION ALL
SELECT 'order_reviews',              COUNT(*) FROM `portfolio-olist-496116.olist_raw.order_reviews`
UNION ALL
SELECT 'products',                   COUNT(*) FROM `portfolio-olist-496116.olist_raw.products`
UNION ALL
SELECT 'sellers',                    COUNT(*) FROM `portfolio-olist-496116.olist_raw.sellers`
ORDER BY row_count DESC;


-- 2. Orders date range & overall volume
SELECT
    MIN(order_purchase_timestamp)           AS first_order,
    MAX(order_purchase_timestamp)           AS last_order,
    COUNT(DISTINCT o.order_id)              AS total_orders,
    COUNT(DISTINCT c.customer_unique_id)    AS unique_customers
FROM `portfolio-olist-496116.olist_raw.orders` o
JOIN `portfolio-olist-496116.olist_raw.customers` c
    USING (customer_id);


-- 3. Null check on critical columns
SELECT
    COUNTIF(order_id IS NULL)               AS null_order_id,
    COUNTIF(customer_id IS NULL)            AS null_customer_id,
    COUNTIF(order_status IS NULL)           AS null_order_status,
    COUNTIF(order_purchase_timestamp IS NULL) AS null_purchase_date,
    COUNTIF(order_delivered_customer_date IS NULL) AS null_delivery_date
FROM `portfolio-olist-496116.olist_raw.orders`;


-- 4. Order status breakdown
SELECT
    order_status,
    COUNT(*)                                        AS total,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM `portfolio-olist-496116.olist_raw.orders`
GROUP BY order_status
ORDER BY total DESC;


-- 5. Duplicate order IDs check
SELECT
    order_id,
    COUNT(*) AS occurrences
FROM `portfolio-olist-496116.olist_raw.orders`
GROUP BY order_id
HAVING COUNT(*) > 1;