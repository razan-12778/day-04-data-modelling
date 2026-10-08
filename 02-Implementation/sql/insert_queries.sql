-- Clear existing data before loading
TRUNCATE TABLE `olist_data_modelling.customers`;
TRUNCATE TABLE `olist_data_modelling.products`;
TRUNCATE TABLE `olist_data_modelling.orders`;
TRUNCATE TABLE `olist_data_modelling.order_items`;


-- Insert customers
INSERT INTO `olist_data_modelling.customers` (
    customer_id,
    customer_unique_id,
    customer_name,
    customer_zip_code,
    customer_segment,
    customer_value_segment,
    customer_since_date,
    customer_segment_effective_date
)
SELECT
    customer_id,
    customer_unique_id,
    customer_name,
    customer_zip_code,
    customer_segment,
    customer_value_segment,
    customer_since_date,
    customer_segment_effective_date
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_segment_effective_date DESC
        ) AS rn
    FROM `olist_data_modelling.raw_sales_transactions`
    WHERE customer_id IS NOT NULL
      AND customer_unique_id IS NOT NULL
      AND customer_name IS NOT NULL
      AND customer_segment IS NOT NULL
      AND customer_value_segment IS NOT NULL
      AND customer_since_date IS NOT NULL
      AND customer_segment_effective_date IS NOT NULL
)
WHERE rn = 1;


-- Insert products
-- Insert products
INSERT INTO `olist_data_modelling.products` (
    product_id,
    product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_price_tier,
    product_shipping_category,
    product_popularity_status
)
SELECT
    product_id,
    COALESCE(product_category_name, 'unknown') AS product_category_name,
    product_name_length,
    product_description_length,
    product_photos_qty,
    product_weight_g,
    product_price_tier,
    product_shipping_category,
    product_popularity_status
FROM (
    SELECT
        product_id,
        product_category_name,
        product_name_length,
        product_description_length,
        product_photos_qty,
        product_weight_g,
        product_price_tier,
        product_shipping_category,
        product_popularity_status,
        ROW_NUMBER() OVER (
            PARTITION BY product_id
            ORDER BY
                CASE
                    WHEN product_category_name IS NOT NULL THEN 0
                    ELSE 1
                END
        ) AS rn
    FROM `olist_data_modelling.raw_sales_transactions`
    WHERE product_id IS NOT NULL
)
WHERE rn = 1;
-- Insert orders
INSERT INTO `olist_data_modelling.orders` (
    order_id,
    customer_id,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_status
)
SELECT DISTINCT
    order_id,
    customer_id,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_customer_date,
    order_status
FROM `olist_data_modelling.raw_sales_transactions`
WHERE order_id IS NOT NULL
  AND customer_id IS NOT NULL;


-- Insert order items
INSERT INTO `olist_data_modelling.order_items` (
    order_id,
    product_id,
    order_item_id,
    item_price,
    freight_value
)
SELECT
    order_id,
    product_id,
    order_item_id,
    CAST(item_price AS NUMERIC),
    CAST(freight_value AS NUMERIC)
FROM `olist_data_modelling.raw_sales_transactions`
WHERE order_id IS NOT NULL
  AND product_id IS NOT NULL
  AND order_item_id IS NOT NULL;
