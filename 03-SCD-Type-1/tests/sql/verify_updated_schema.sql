SELECT
  'customers' as table_name,
  COUNT(*) as total_records,
  COUNT(record_created_date) as populated_created,
  COUNT(record_last_updated) as populated_updated,
  COUNT(data_version) as populated_version
FROM `${GCP_PROJECT_ID}.olist_data_modelling.customers`

UNION ALL

SELECT
  'products' as table_name,
  COUNT(*) as total_records,
  COUNT(record_created_date) as populated_created,
  COUNT(record_last_updated) as populated_updated,
  COUNT(data_version) as populated_version
FROM `${GCP_PROJECT_ID}.olist_data_modelling.products`

UNION ALL

SELECT
  'orders' as table_name,
  COUNT(*) as total_records,
  COUNT(record_created_date) as populated_created,
  COUNT(record_last_updated) as populated_updated,
  COUNT(data_version) as populated_version
FROM `${GCP_PROJECT_ID}.olist_data_modelling.orders`

UNION ALL

SELECT
  'order_items' as table_name,
  COUNT(*) as total_records,
  COUNT(record_created_date) as populated_created,
  COUNT(record_last_updated) as populated_updated,
  COUNT(data_version) as populated_version
FROM `${GCP_PROJECT_ID}.olist_data_modelling.order_items`

ORDER BY table_name;
