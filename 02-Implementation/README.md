# 🎯 Goal

**Database Implementation** is where your data model design comes to life! Having completed the logical model and ERD in the previous challenge, you'll now translate that design into working BigQuery tables using **Data Definition Language (DDL)** and populate them with data using **Data Manipulation Language (DML)**.

This challenge focuses on the **Physical Model** step of the data modelling process - taking your normalized schema design and implementing it as actual database tables with proper data types, constraints, and relationships.

You'll practice essential Data Engineering skills by:
- Writing **CREATE TABLE** statements with appropriate BigQuery data types and constraints
- Designing **INSERT queries** to extract and transform data from denormalized sources
- Validating your implementation to ensure data integrity and completeness

The goal is to have four normalized tables (`customers`, `products`, `orders`, `order_items`) populated with clean, structured data ready for analytics and reporting.

<br>

# 0️⃣ Setup

## 0.1. Environment variables

Make sure to copy across your `.env` from the previous challenge, or make a copy of the `.env.sample` in this challenge and fill out the values.

Don't forget to load your environment variables with:

```bash
direnv reload
```

## 0.2. Verify Your Source Data

Confirm your denormalized data is available in BigQuery by executing the following in the BigQuery console:

```sql
SELECT COUNT(*) as total_transactions
FROM `olist_data_modelling.raw_sales_transactions`
```

You should see a count of transactions (112 650) available for processing.

<br>

# 1️⃣ DDL Design 🏗️

Now it's time to implement your normalized schema using BigQuery DDL! You'll create four tables based on your schema and ERD from the previous challenge.

❓ **Your Task**: Create DDL statements for each normalized table:

1. **customers** - Customer master data
2. **products** - Product catalog information
3. **orders** - Order header information
4. **order_items** - Individual line items within orders

## 1.1. BigQuery Data Type Mapping

BigQuery has slightly different data types compared to transactional databases like Postgres and MySQL.

Use the following data type mappings for BigQuery DDL:

<table>
  <thead>
    <tr>
      <th>DBML Type</th>
      <th>BigQuery Type</th>
      <th>Use For</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>VARCHAR(n)</code></td>
      <td><code>STRING</code></td>
      <td>Text fields, IDs</td>
    </tr>
    <tr>
      <td><code>INTEGER</code></td>
      <td><code>INT64</code></td>
      <td>Whole numbers</td>
    </tr>
    <tr>
      <td><code>FLOAT</code></td>
      <td><code>FLOAT64</code></td>
      <td>Decimal numbers</td>
    </tr>
    <tr>
      <td><code>DECIMAL(p,s)</code></td>
      <td><code>NUMERIC(p,s)</code></td>
      <td>Precise decimal (prices)</td>
    </tr>
    <tr>
      <td><code>TIMESTAMP</code></td>
      <td><code>TIMESTAMP</code></td>
      <td>Timestamps</td>
    </tr>
  </tbody>
</table>

## 1.2. DDL Implementation

In the `sql/` directory, create a file called `ddl_queries.sql` with your **CREATE TABLE** statements.

💡 Note that BigQuery doesn't enforce `PRIMARY KEY` constraints, but they are worth adding to your table for readability and enabling additional tooling. BigQuery (and most other warehouses) also do not allow a table to have two primary keys, for the `order_items` table, you can omit them in this challenge. The `NOT ENFORCED` statement is required so user acknowledge that BigQuery does not enforce Primary Keys.

❓ Write DDL for each table following this template:

```sql
-- Create customers table
CREATE TABLE `olist_data_modelling.customers` (
    customer_id STRING NOT NULL PRIMARY KEY NOT ENFORCED,
    customer_unique_id STRING NOT NULL,
    -- Add remaining columns with appropriate data types
);

-- Create products table
CREATE TABLE `olist_data_modelling.products` (
    -- Define your product columns here
);

-- Create orders table
CREATE TABLE `olist_data_modelling.orders` (
    -- Define your order columns here
);

-- Create order_items table
CREATE TABLE `olist_data_modelling.order_items` (
    -- Define your order_items columns here
);
```

<details>
<summary markdown='span'>💡 BigQuery DDL Tips</summary>

- BigQuery doesn't enforce PRIMARY KEY constraints, but you should still define **NOT NULL** constraints for relevant columns
- Use `STRING` instead of `VARCHAR(n)` in BigQuery - it's more flexible
- For monetary values, prefer `NUMERIC(10,2)` over `FLOAT64` for precision
- `TIMESTAMP` columns can be nullable if the event hasn't occurred yet (e.g., order_delivered_customer_date)
- Consider adding table descriptions using `OPTIONS(description="Table purpose")`
- Consider using `CREATE OR REPLACE TABLE` so you don't have to manually delete tables as you incrementally work towards your solution
</details>

## 1.3. Execute Your DDL

Run your DDL queries in the BigQuery console as a SQL script, either all together or one at a time. Alternatively you can use the `bq` CLI tool to execute SQL scripts:

```bash
# Execute your DDL file
bq query --use_legacy_sql=false < path/to/sql_script.sql

# The above command is the same as:
# cat path/to/sql_script.sql | bq query --use_legacy_sql=false
```

<br>

# 2️⃣ Data Loading with INSERT Queries 📊

With your normalized tables created, it's time to populate them with data from the denormalized source table.

You'll write **INSERT** queries that extract distinct values for each entity type and insert them into the appropriate normalized tables.

## 2.1. Data Loading Strategy

The loading process follows this sequence:
1. **customers** first (no dependencies)
2. **products** next (no dependencies)
3. **orders** third (depends on customers)
4. **order_items** last (depends on orders and products)

❓ **Your Task**: Create a file called `insert_queries.sql` with INSERT statements for each table.


## 2.2. Customers Table Loading

The `customers` table is a bit special, because we are taking a **snapshot** in time and the `customer` table has some inherent temporal aspects. The decision from management is to take the most recent customer data to insert into the `customers` table.

As an example, here is how you could extract the **most recent, distinct customer records** from the denormalized data:

```sql
-- Insert customers data
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
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    -- Add remaining customer columns from raw_sales_transactions
    -- Use DISTINCT to avoid duplicate customer records
FROM (
    -- This subquery is specific to extracting the most recent records
    -- otherwise you could just reference the table and move the WHERE statements outside
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY customer_id
            ORDER BY customer_segment_effective_date DESC
        ) as rn
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
```

## 2.3. Products Table Loading

❓ **Your Task**: Write an INSERT statement for the products table that:
- Extracts distinct product records
- Includes all product-related columns from your schema
- Filters out any NULL product_id values

## 2.4. Orders Table Loading

❓ **Your Task**: Write an INSERT statement for the orders table that:
- Extracts distinct order records (one row per `order_id`)
- Links to customer_id as foreign key
- Includes order status and timestamp information

## 2.5. Order Items Table Loading

❓ **Your Task**: Write an INSERT statement for the order_items table that:
- Preserves all individual line items (no DISTINCT needed)
- Links to both order_id and product_id as foreign keys
- Includes pricing and freight information

<details>
<summary markdown='span'>💡 INSERT Query Tips</summary>

- Use `SELECT DISTINCT` for master data tables (customers, products, orders) to avoid duplicates
- Don't use `DISTINCT` for **order_items** - you want to preserve individual line items
- Always include `WHERE` clauses to filter out NULL key values
- Consider the order of execution - customers and products first, then orders, finally order_items
- You might need to cast values.
- Test each `INSERT` individually before running all together
- If you inserted data, but made a mistake. Recreate an empty table using `CREATE OR REPLACE` in your DML script.
</details>

## 2.6. Execute Your INSERT Queries

Run your DML queries in the BigQuery console as a SQL script, either all together or execute them one at a time. Alternatively you can use the `bq` CLI tool to execute SQL scripts:

```bash
# Execute your insert queries
bq query --use_legacy_sql=false < path/to/sql_script.sql
```

<br>

# 3️⃣ Validation 🔍

To verify your implementation is correct, use the provided validation queries. These check data completeness, referential integrity, and business logic.

❓ For each query, examine it to understand what it is doing and execute it.

## 3.1. Row Count Validation

```sql
-- Verify row counts make sense
SELECT
    'customers' as table_name,
    COUNT(*) as row_count
FROM `olist_data_modelling.customers`

UNION ALL

SELECT
    'products' as table_name,
    COUNT(*) as row_count
FROM `olist_data_modelling.products`

UNION ALL

SELECT
    'orders' as table_name,
    COUNT(*) as row_count
FROM `olist_data_modelling.orders`

UNION ALL

SELECT
    'order_items' as table_name,
    COUNT(*) as row_count
FROM `olist_data_modelling.order_items`

UNION ALL

SELECT
    'raw_sales_transactions' as table_name,
    COUNT(*) as row_count
FROM `olist_data_modelling.raw_sales_transactions`;
```

**Expected Result**: `order_items` should have the same row count as `raw_sales_transactions` because it's a junction table with a composite key. Other tables should have fewer rows due to normalization, particularly `products`.

🤔 It is weird that `orders` and `customers` have the same number of records, implying that each order is from a unique customer with no customers placing more than one order. Feel free to confirm for yourself with `COUNT(DISTINCT(...))` queries on the `raw_sales_transactions` table.

<!-- in a two year period: 2016-09-04 to 2018-09-03 -->

## 3.2. Referential Integrity Validation

```sql
-- Check for orphaned records (foreign key violations)

-- Orders without customers
SELECT COUNT(*) as orphaned_orders
FROM `olist_data_modelling.orders` o
LEFT JOIN `olist_data_modelling.customers` c
ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Order items without orders
SELECT COUNT(*) as orphaned_order_items_orders
FROM `olist_data_modelling.order_items` oi
LEFT JOIN `olist_data_modelling.orders` o
ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;
```

**Expected Result**: All counts should be 0 (no orphaned records).

## 3.3. Data Completeness Validation

```sql
-- Check for NULL values in key columns
SELECT
    'customers' as table_name,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN customer_name IS NULL THEN 1 ELSE 0 END) as null_names
FROM `olist_data_modelling.customers`

UNION ALL

SELECT
    'products' as table_name,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN product_category_name IS NULL THEN 1 ELSE 0 END) as null_names
FROM `olist_data_modelling.products`

UNION ALL

SELECT
    'orders' as table_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN customer_id IS NULL THEN 1 ELSE 0 END) as null_names
FROM `olist_data_modelling.orders`

UNION ALL

SELECT
    'order_items' as table_name,
    SUM(CASE WHEN order_id IS NULL THEN 1 ELSE 0 END) as null_ids,
    SUM(CASE WHEN product_id IS NULL THEN 1 ELSE 0 END) as null_names
FROM `olist_data_modelling.order_items`

ORDER BY table_name;

```

**Expected Result**: All null counts should be 0 for required fields.

## 3.4. Business Logic Validation

```sql
-- Verify order totals match when aggregated from order_items
WITH order_totals AS (
    SELECT
        order_id,
        SUM(item_price + freight_value) as calculated_total,
        COUNT(*) as item_count
    FROM `olist_data_modelling.order_items`
    GROUP BY order_id
),
original_totals AS (
    SELECT DISTINCT
        order_id,
        order_total_amount,
        order_total_items
    FROM `olist_data_modelling.raw_sales_transactions`
)
SELECT
    COUNT(*) as mismatched_orders
FROM order_totals ot
JOIN original_totals orig ON ot.order_id = orig.order_id
WHERE ABS(ot.calculated_total - orig.order_total_amount) > 0.01
   OR ot.item_count != orig.order_total_items;
```

**Expected Result**: Should be 0 mismatched orders.

<br>

# 🏁 Finishing Up

By the end of this challenge, you have successfully completed:
✅ **DDL Implementation:** Created normalized tables in BigQuery with appropriate data types and constraints
✅ **Data Loading:** Populated tables using INSERT queries that extract and transform data from denormalized sources
✅ **Referential Integrity:** Established proper foreign key relationships between entities
✅ **Data Validation:** Verified your implementation maintains data completeness and business logic consistency

You've now experienced the complete data modelling lifecycle - from analysis and design to physical implementation. These skills are fundamental for Data Engineers working with:
- **ETL/ELT Pipelines:** Transforming raw data into structured analytics-ready formats
- **Data Warehouse Design:** Creating efficient storage structures for analytical workloads
- **Database Migration:** Moving from legacy systems to modern cloud data platforms
- **Schema Evolution:** Managing database changes as business requirements evolve

Your normalized schema provides a solid foundation for analytics, reporting, and machine learning use cases while maintaining data integrity and reducing storage costs.

In the next challenge we'll explore **Slowly Changing Dimensions** to handle historical data that changes over time!

🧪 To validate your implementation, run:

```bash
make test
```

And don't forget to push your code to Github to track your progress on Kitt!

<br>
