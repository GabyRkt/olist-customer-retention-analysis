-- ============================================================
-- Query 06 — Customer Lifetime Value Ranking
-- Goal: Rank customers by total spend and segment into tiers
-- Window functions: RANK(), NTILE(), SUM() OVER()
-- Stakeholder: Head of Growth
-- ============================================================
 
WITH customer_revenue AS (
    -- Calculate total spend per customer
    SELECT
        c.customer_unique_id,
        COUNT(DISTINCT o.order_id)          AS total_orders,
        ROUND(SUM(p.payment_value), 2)      AS total_spent,
        MIN(CAST(CAST(o.order_purchase_timestamp AS TIMESTAMP) AS DATE)) AS first_order_date,
        MAX(CAST(CAST(o.order_purchase_timestamp AS TIMESTAMP) AS DATE)) AS last_order_date
    FROM `portfolio-olist-496116.olist_raw.orders` o
    JOIN `portfolio-olist-496116.olist_raw.customers` c
        USING (customer_id)
    JOIN `portfolio-olist-496116.olist_raw.order_payments` p
        USING (order_id)
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
 
customer_ranked AS (
    SELECT
        customer_unique_id,
        total_orders,
        total_spent,
        first_order_date,
        last_order_date,
        -- Rank customers by total spend
        RANK() OVER (ORDER BY total_spent DESC)             AS spend_rank,
        -- Segment into 10 deciles
        NTILE(10) OVER (ORDER BY total_spent DESC)          AS spend_decile,
        -- Total revenue across all customers for share calculation
        SUM(total_spent) OVER ()                            AS overall_revenue
    FROM customer_revenue
)
 
SELECT
    spend_decile,
    CASE spend_decile
        WHEN 1  THEN 'Top 10%'
        WHEN 2  THEN 'Top 20%'
        WHEN 3  THEN 'Top 30%'
        ELSE 'Bottom 70%'
    END                                                         AS segment,
    COUNT(DISTINCT customer_unique_id)                          AS nb_customers,
    ROUND(AVG(total_orders), 2)                                 AS avg_orders,
    ROUND(AVG(total_spent), 2)                                  AS avg_spent,
    ROUND(SUM(total_spent), 2)                                  AS segment_revenue,
    ROUND(SUM(total_spent) * 100.0 / MAX(overall_revenue), 2)  AS revenue_share_pct
FROM customer_ranked
GROUP BY spend_decile, segment
ORDER BY spend_decile;