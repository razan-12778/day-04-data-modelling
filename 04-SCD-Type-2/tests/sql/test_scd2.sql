SELECT customer_id, COUNT(*) as versions
FROM `${GCP_PROJECT_ID}.olist_data_modelling.customers_scd2`
GROUP BY customer_id
HAVING COUNT(*) > 1;
