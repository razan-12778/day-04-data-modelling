
INSERT INTO `olist_data_modelling.customers_scd2`
SELECT
    customer_id,
    customer_unique_id,
    customer_name,
    customer_zip_code,
    customer_segment,
    customer_value_segment,
    customer_since_date,
    customer_segment_effective_date,
    record_created_date,
    record_last_updated,
    data_version,
    CONCAT(customer_id, '_v', CAST(data_version AS STRING)) AS customer_key,
    customer_segment_effective_date AS effective_date,
    CAST(NULL AS TIMESTAMP) AS end_date,
    TRUE AS is_current,
    data_version AS version_number
FROM `olist_data_modelling.customers`;


