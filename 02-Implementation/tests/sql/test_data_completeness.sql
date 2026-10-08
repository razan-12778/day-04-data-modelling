-- Data Completeness Validation Query
-- Checks for NULL values in key columns
-- All null counts should be 0 for required fields

SELECT
    'customers' as table_name,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) as null_names
FROM `${GCP_PROJECT_ID}.olist_data_modelling.customers`

UNION ALL

SELECT
    'products' as table_name,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN product_category_name IS NULL THEN 1 ELSE 0 END) as null_names
FROM `${GCP_PROJECT_ID}.olist_data_modelling.products`

UNION ALL

SELECT
    'orders' as table_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_names
FROM `${GCP_PROJECT_ID}.olist_data_modelling.orders`

UNION ALL

SELECT
    'order_items' as table_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_names
FROM `${GCP_PROJECT_ID}.olist_data_modelling.order_items`

ORDER BY table_name;
