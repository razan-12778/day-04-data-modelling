
-- Update customers audit fields
UPDATE `olist_data_modelling.customers` AS customers
SET
    record_created_date = source.record_created_date,
    record_last_updated = source.record_last_updated,
    data_version = source.data_version
FROM (
    SELECT
        customer_id,
        record_created_date,
        record_last_updated,
        data_version
    FROM (
        SELECT
            customer_id,
            record_created_date,
            record_last_updated,
            data_version,
            ROW_NUMBER() OVER (
                PARTITION BY customer_id
                ORDER BY record_last_updated DESC
            ) AS rn
        FROM `olist_data_modelling.raw_sales_transactions`
        WHERE customer_id IS NOT NULL
    )
    WHERE rn = 1
) AS source
WHERE customers.customer_id = source.customer_id;


-- Update products audit fields
UPDATE `olist_data_modelling.products` AS products
SET
    record_created_date = source.record_created_date,
    record_last_updated = source.record_last_updated,
    data_version = source.data_version
FROM (
    SELECT
        product_id,
        record_created_date,
        record_last_updated,
        data_version
    FROM (
        SELECT
            product_id,
            record_created_date,
            record_last_updated,
            data_version,
            ROW_NUMBER() OVER (
                PARTITION BY product_id
                ORDER BY record_last_updated DESC
            ) AS rn
        FROM `olist_data_modelling.raw_sales_transactions`
        WHERE product_id IS NOT NULL
    )
    WHERE rn = 1
) AS source
WHERE products.product_id = source.product_id;


-- Update orders audit fields
UPDATE `olist_data_modelling.orders` AS orders
SET
    record_created_date = source.record_created_date,
    record_last_updated = source.record_last_updated,
    data_version = source.data_version
FROM (
    SELECT
        order_id,
        record_created_date,
        record_last_updated,
        data_version
    FROM (
        SELECT
            order_id,
            record_created_date,
            record_last_updated,
            data_version,
            ROW_NUMBER() OVER (
                PARTITION BY order_id
                ORDER BY record_last_updated DESC
            ) AS rn
        FROM `olist_data_modelling.raw_sales_transactions`
        WHERE order_id IS NOT NULL
    )
    WHERE rn = 1
) AS source
WHERE orders.order_id = source.order_id;


-- Update order_items audit fields
UPDATE `olist_data_modelling.order_items` AS order_items
SET
    record_created_date = source.record_created_date,
    record_last_updated = source.record_last_updated,
    data_version = source.data_version
FROM (
    SELECT
        order_id,
        product_id,
        order_item_id,
        record_created_date,
        record_last_updated,
        data_version
    FROM (
        SELECT
            order_id,
            product_id,
            order_item_id,
            record_created_date,
            record_last_updated,
            data_version,
            ROW_NUMBER() OVER (
                PARTITION BY order_id, product_id, order_item_id
                ORDER BY record_last_updated DESC
            ) AS rn
        FROM `olist_data_modelling.raw_sales_transactions`
        WHERE order_id IS NOT NULL
          AND product_id IS NOT NULL
          AND order_item_id IS NOT NULL
    )
    WHERE rn = 1
) AS source
WHERE order_items.order_id = source.order_id
  AND order_items.product_id = source.product_id
  AND order_items.order_item_id = source.order_item_id;
