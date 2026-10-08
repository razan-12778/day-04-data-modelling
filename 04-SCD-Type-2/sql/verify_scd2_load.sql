SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_records,
    COUNT(CASE WHEN end_date IS NULL THEN 1 END) as records_without_end_date,
    COUNT(DISTINCT customer_id) as unique_customers
FROM `olist_data_modelling.customers_scd2`;
