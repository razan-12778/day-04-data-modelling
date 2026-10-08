-- ##### Verify order totals match when aggregated from order_items #####
WITH order_totals AS (
    SELECT
        order_id,
        SUM(item_price + freight_value) as calculated_total,
        COUNT(*) as item_count
    FROM `{project_id}.olist_data_modelling.order_items`
    GROUP BY order_id
),
original_totals AS (
    SELECT DISTINCT
        order_id,
        order_total_amount,
        order_total_items
    FROM `{project_id}.olist_data_modelling.raw_sales_transactions`
)
SELECT
    COUNT(*) as mismatched_orders
FROM order_totals ot
JOIN original_totals orig ON ot.order_id = orig.order_id
WHERE ABS(ot.calculated_total - orig.order_total_amount) > 0.01
   OR ot.item_count != orig.order_total_items;
