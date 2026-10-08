-- Create customers table
CREATE OR REPLACE TABLE `olist_data_modelling.customers` (
    customer_id STRING NOT NULL PRIMARY KEY NOT ENFORCED,
    customer_unique_id STRING NOT NULL,
    customer_name STRING NOT NULL,
    customer_zip_code INT64,
    customer_segment STRING,
    customer_value_segment STRING,
    customer_since_date TIMESTAMP,
    customer_segment_effective_date TIMESTAMP
);

-- Create products table
CREATE OR REPLACE TABLE `olist_data_modelling.products` (
    product_id STRING NOT NULL PRIMARY KEY NOT ENFORCED,
    product_category_name STRING,
    product_name_length FLOAT64,
    product_description_length FLOAT64,
    product_photos_qty FLOAT64,
    product_weight_g FLOAT64,
    product_price_tier STRING,
    product_shipping_category STRING,
    product_popularity_status STRING
);

-- Create orders table
CREATE OR REPLACE TABLE `olist_data_modelling.orders` (
    order_id STRING NOT NULL PRIMARY KEY NOT ENFORCED,
    customer_id STRING NOT NULL,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_status STRING
);

-- Create order_items table
CREATE OR REPLACE TABLE `olist_data_modelling.order_items` (
    order_id STRING NOT NULL,
    product_id STRING NOT NULL,
    order_item_id INT64 NOT NULL,
    item_price NUMERIC(10,2),
    freight_value NUMERIC(10,2)
);
