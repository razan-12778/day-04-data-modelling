ALTER TABLE `olist_data_modelling.customers`
ADD COLUMN record_created_date TIMESTAMP,
ADD COLUMN record_last_updated TIMESTAMP,
ADD COLUMN data_version INT64;

ALTER TABLE `olist_data_modelling.products`
ADD COLUMN record_created_date TIMESTAMP,
ADD COLUMN record_last_updated TIMESTAMP,
ADD COLUMN data_version INT64;

ALTER TABLE `olist_data_modelling.orders`
ADD COLUMN record_created_date TIMESTAMP,
ADD COLUMN record_last_updated TIMESTAMP,
ADD COLUMN data_version INT64;

ALTER TABLE `olist_data_modelling.order_items`
ADD COLUMN record_created_date TIMESTAMP,
ADD COLUMN record_last_updated TIMESTAMP,
ADD COLUMN data_version INT64;