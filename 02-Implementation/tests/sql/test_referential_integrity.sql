SELECT
    'orders_without_customers' as validation_type,
    COUNT(*) as orphaned_count
FROM `${GCP_PROJECT_ID}.olist_data_modelling.orders` o
LEFT JOIN `${GCP_PROJECT_ID}.olist_data_modelling.customers` c
ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

-- Check for order items without orders
SELECT
    'order_items_without_orders' as validation_type,
    COUNT(*) as orphaned_count
FROM `${GCP_PROJECT_ID}.olist_data_modelling.order_items` oi
LEFT JOIN `${GCP_PROJECT_ID}.olist_data_modelling.orders` o
ON oi.order_id = o.order_id
WHERE o.order_id IS NULL

ORDER BY validation_type;
