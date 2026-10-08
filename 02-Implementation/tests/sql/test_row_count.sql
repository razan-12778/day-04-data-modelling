SELECT
    'customers' as table_name,
    COUNT(*) as row_count
FROM `{project_id}.olist_data_modelling.customers`

UNION ALL

SELECT
    'products' as table_name,
    COUNT(*) as row_count
FROM `{project_id}.olist_data_modelling.products`

UNION ALL

SELECT
    'orders' as table_name,
    COUNT(*) as row_count
FROM `{project_id}.olist_data_modelling.orders`

UNION ALL

SELECT
    'order_items' as table_name,
    COUNT(*) as row_count
FROM `{project_id}.olist_data_modelling.order_items`

UNION ALL

SELECT
    'raw_sales_transactions' as table_name,
    COUNT(*) as row_count
FROM `{project_id}.olist_data_modelling.raw_sales_transactions`;
