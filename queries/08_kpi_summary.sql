SELECT
    (
        SELECT COUNT(DISTINCT c.customer_unique_id)
        FROM `portfolio-olist-496116.olist_raw.orders` o
        JOIN `portfolio-olist-496116.olist_raw.customers` c
            USING (customer_id)
        WHERE o.order_status = 'delivered'
    )                                               AS total_unique_customers,
    ROUND(AVG(churn_rate), 2)                       AS avg_churn_rate,
    ROUND(AVG(retention_rate), 2)                   AS avg_retention_rate,
    SUM(returning_customers)                        AS total_returning_customers,
    SUM(churned_customers)                          AS total_churned_customers
FROM `portfolio-olist-496116.olist_analytics.churn_rate` 