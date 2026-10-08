# 🎯 Goal

**Data modelling** is the process of creating a visual representation of data and its relationships within a system. It serves as the blueprint for database design and helps ensure data integrity, efficiency, and maintainability.

The data modelling process typically follows the process of:
1. **Analyse the Data**: Understand the data, don't make assumptions
2. **Conceptual Model**: High-level business entities and relationships
3. **Logical Model**: Detailed attributes and normalized structure. Usually create Entity Relationship Diagram as part of this step.
4. **Physical Model**: Implementation-specific details for database creation

The goal of this exercise is to design a normalized database schema from a heavily denormalized e-commerce sales transaction data by following the first three steps of the process: **Data Analysis**, **Conceptual Modelling**, and **Logical Modelling**, including drawing the Entity Relationship Diagram.

You'll practice the fundamentals of data modelling by transforming a flat, redundant sales transaction dataset into a well-structured, normalized schema following **Third Normal Form (3NF)**. 3NF is the gold standard **OLTP Design Pattern** because it maintains data integrity and is storage efficient. It's important to understand normalisation before learning how to **strategically denormalise for analytics, or OLAP workloads.**

The data store we will be using is **BigQuery**, GCP's Data Warehouse.

---

This is a conceptual challenge that is perfect for dividing and conquering! Work closely with your buddy or in a small group to lighten the load and compare notes 🚀

<br>

# 0️⃣ Setup

## 0.1. Data

The data you will be working with is **E-Commerce** sales transactions from the [Brazilian E-Commerce Platform Olist Public Dataset 🔗](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). For the challenges in this unit, the data has been intentionally de-normalised into a single large table.

To get started, download the CSV file with the following:

```bash
curl -o ./data/olist_sales_transactions.csv https://wagon-public-datasets.s3.amazonaws.com/data-engineering/0203-data-modelling/denormalised_olist_sales_transactions-v2.csv
```

## 0.2. Create a BigQuery Dataset and Table

It will be useful to have the data in a table to query against during your analysis and modelling.

To start with, create a `.env` from the `.env.sample` and fill with relevant values. Don't forget to reload your `.env` environment variables with:

```bash
direnv reload
```

To create a BigQuery dataset, use the following `bq` CLI command:

```bash
bq mk --location=$GCP_REGION --dataset $GCP_PROJECT_ID:olist_data_modelling
```

And to create a table and import the data:

```bash
bq load \
    --autodetect \
    --source_format=CSV \
    --skip_leading_rows=1 \
    --field_delimiter="," \
    --location=$GCP_REGION \
    olist_data_modelling.raw_sales_transactions \
    ./data/olist_sales_transactions.csv
```

And if you navigate to the BigQuery Console at this [link here 🔗](https://console.cloud.google.com/bigquery) you should see a dataset named: `olist_data_modelling` with a table named: `raw_sales_transactions` that you can query!

## 0.3. Modelling Tools

Some recommended tools for modelling:
- **For Conceptual Modelling:** we strongly recommend using a free form drawing tool like [excalidraw 🔗](https://excalidraw.com/), [draw.io 🔗](https://www.drawio.com/), or even a pen and paper.
- **For Logical Modelling and ERD Design:** you will be using [dbdiagram.io 🔗](https://www.dbdiagram.io). At the time of writing, you do not need an account, and are able to define your ERD using **Database Markup Language (DBML)**, a simple and intuitive syntax to define your schema and ERDs as code.

<br>

# 1️⃣ Analyse the Data 🔍

Before doing any sort of modelling, understanding the data you are working with is key!

First, examine the provided data, `olist_sales_transactions`, to understand its current structure and identify the data quality issues that normalization will address.

❓ **Your Task**: Analyze the data's structure by answering these questions:

1. How many columns does the dataset contain?
2. What types of entities can you identify based on the column names?
3. Which columns appear to contain redundant data?
4. What relationships exist between different data elements?

❗ For the moment, you can ignore the three audit fields: `record_created_date`, `record_last_updated`, `data_version`. We'll be using them when we start integrating temporal management into our warehouse. You can think of this exercise as creating a _snapshot in time_.

<details>
<summary markdown='span'>💡 Column Descriptions</summary>

Descriptions are in the format of:
- `column_name`: Data Type - Description

Column Descriptions:
- `transaction_id`: String (UUID-like) - Unique identifier for each transaction record
- `order_id`: String (UUID-like) - Unique identifier for each customer order
- `order_item_id`: Integer - Sequential number identifying each line item within an order
- `order_purchase_timestamp`: Timestamp - Date and time when the customer placed the order
- `order_approved_at`: Timestamp - Date and time when the order was approved for processing
- `order_delivered_customer_date`: Timestamp - Date and time when the order was delivered to the customer
- `order_status`: String(Enumerated) - Current status of the order in the fulfilment process
- `customer_id`: String (UUID-like) - Unique identifier for each customer account
- `customer_unique_id`: String (UUID-like) - Alternative unique identifier for customer (may represent different system ID)
- `customer_name`: String - Cryptographically anonymized identifier for the customer, relationship preserved.
- `customer_zip_code`: Integer - Postal/ZIP code of customer's address
- `customer_segment`: String(Enumerated) - Customer classification based on business rules
- `customer_value_segment`: String(Enumerated)- Customer classification based on spending behaviour
- `customer_since_date`: Date - Date when the customer first registered or made their first purchase
- `customer_segment_effective_date`: Date - Date when the current customer segment classification became effective
- `product_id`: String (UUID-like) - Unique identifier for each product
- `product_category_name`: String - Category or classification of the product
- `product_name_length`: Integer/Float - Length of the product name in characters
- `product_description_length`: Integer/Float- Length of the product description in characters
- `product_photos_qty`: Integer/Float - Number of photos/images associated with the product
- `product_weight_g`: Integer/Float - Weight of the product in grams
- `product_price_tier`: String(Enumerated) - Price classification or tier of the product
- `product_shipping_category`: String(Enumerated) - Shipping classification affecting delivery options/costs
- `product_popularity_status`: String(Enumerated) - Classification of product popularity or demand level
- `product_price_tier_effective_date`: Date - Date when the current price tier classification became effective
- `item_price`: Float - Unit price of the product for this specific line item
- `freight_value`: Float - Shipping/freight cost associated with this line item
- `item_total`: Float - Total cost for this line item (item_price + freight_value)
- `order_total_amount`: Float - Total monetary value of the entire order (sum of all line items)
- `order_total_items`: Integer - Total number of line items in the order
- `order_average_item_price`: Float - Average price per item in the order (order_total_amount / order_total_items)
- `order_customer_segment`: String - Customer segment at the time this order was placed
- `record_created_date`: Timestamp - AUDIT FIELD: Date and time when this record was first created in the system
- `record_last_updated`: Timestamp - AUDIT FIELD: Date and time when this record was last modified
- `data_version`: Integer - AUDIT FIELD: Version number for this record, incremented with each update

Data types like: `String (Enumerated)` and `String (UUID-like)` are just SQL `Strings` in BigQuery. The additional information is for your context.

A Enumerated String restricts a column to storing only a value from a predefined list of string options, such as: `Low Value`, `Medium Value`, `High Value`.
</details>

<br>

<details>
<summary markdown='span'>💡 Hints</summary>

- Look for column naming patterns that suggest different entity types (e.g., `customer_*`, `order_*`, `product_*`)
- What columns might serve as primary or foreign keys
- Are there repeated data patterns that could indicate normalization opportunities
- Consider which columns logically belong together as attributes of the same entity
</details>

<br>

# 2️⃣ Conceptual Model 💭

A conceptual model is the highest level, most abstract view of your data. The conceptual model focuses on identifying the core business entities and their high-level relationships without getting into detailed attributes (specific column names, column data types) or implementation specifics.

❓ **Your Task**: Create a conceptual model by identifying:

1. **Core Business Entities**: What are the main "things" in this e-commerce domain?
2. **Primary Relationships**: How do these entities relate to each other? Are they one-to-one, one-to-many, or many-to-many relationships?
3. **Relationship Cardinality**: What are the one-to-one, one-to-many, or many-to-many relationships?


❗ For the moment, you can ignore the three audit fields: `record_created_date`, `record_last_updated`, `data_version`. We'll be using them when we start integrating temporal management into our warehouse.

<details>
<summary markdown='span'>💡 Hints</summary>

- Think about the real-world e-commerce business process: customers place orders, orders contain items, items are specific products
- Consider the relationship between customers and orders - can a customer have multiple orders?
- Think about the relationship between orders and products - can an order contain multiple products? Can a product appear in multiple orders?
- If two entities have a many-to-many relationship, you will need an entity to act as a junction between them
</details>

🎯 **Expected Outcome**: You should identify 4 main entities with clear relationships between them. The relationships should reflect typical e-commerce patterns where entities are connected through foreign-key relationships.

<br>

# 3️⃣ Logical Model & ERD 📋

With the high level conceptual model complete, it's time to extend it to add some more detail and structure.

For this exercise, you'll use [dbdiagram.io 🔗](https://www.dbdiagram.io) to create and define your Logical Model. This tool is specifically designed for database schema definition and visualization and will help you create professional ERDs that clearly show your normalized design. **dbdiagram.io** uses the simple and intuitive **DBML** syntax to define schema. The benefit is that by defining your schema as **DBML**, the tool will automatically generate a visual ERD!

The small toy project that is present when you open **dbdiagram.io** should be enough for you to create your own schema. If you need more detail, refer to the documentation at this [link here 🔗](https://dbml.dbdiagram.io/docs)

At time of writing **dbdiagram.io** does not require an account for basic use. If you do create an account you can export DDL SQL queries based on your schema which can be useful.

## 3.1. Designing the Normalized Schema

The logical model translates your conceptual understanding into a detailed, normalized schema design that eliminates redundancy while preserving all necessary information.

❓ **Your Task**: Create a logical model that includes:

1. **Entity Definition**: List all attributes (columns) for each of the 4 entities
2. **Primary Key Selection**: Choose appropriate primary keys for each table
3. **Attribute Data Types**: Choose an appropriate SQL data type from the rule of thumb below
4. **Attribute Constraints**: Apply constraints to your attributes (columns, things like `Not Null`, `Unique`
5. **Foreign Key Relationships**: Define how entities connect to each other. Use correct symbols for 1:1, 1:N, N:1, and/or N:N relationships
6. **Normalization Verification**: Ensure your design meets Third Normal Form requirements

The following are a general rule of thumb for SQL data types:
- **IDs**: `VARCHAR(50)` for string-based IDs, `INTEGER` for numeric sequences
- **Timestamps**: `TIMESTAMP` or `DATETIME` for time/date values respectively
- **Prices/Money**: `DECIMAL(10,2)` for currency values to avoid floating-point precision issues
- **Descriptions**: `TEXT` for long text fields, `VARCHAR(255)` for shorter strings
- **Status Fields**: `VARCHAR(20)` for status enumerations
- **Weights/Measurements**: `DECIMAL` for precise numeric measurements
- **Boolean Flags**: `BOOLEAN` for true/false values

❗ For the moment, ignore the three audit fields: `record_created_date`, `record_last_updated`, `data_version`. We'll be using them when we start integrating temporal management into our warehouse.

<details>
<summary markdown='span'>💡 General Hints</summary>

- Group related columns from the denormalized dataset into logical entities
- Look for natural primary keys in the data (like `customer_id`, `order_id`, `product_id`)
- You will need a table to connect `orders` and `products` that may not fit 3NF
- Consider which entity should "own" calculated fields like totals
- Pay attention to temporal attributes (dates) and which entity they logically belong to
- Remember that foreign keys in one table should reference primary keys in another table

---

A reminder of the definition of the first three normal forms:

**First Normal Form (1NF)**:
- All attributes contain atomic (single) values
- No repeating groups or arrays in columns
- Each row must be unique

**Second Normal Form (2NF)**:
- Must be in 1NF
- All non-key attributes must be fully dependent on the primary key
- No partial dependencies on composite keys

**Third Normal Form (3NF)**:
- Must be in 2NF
- No transitive dependencies (non-key attributes should not depend on other non-key attributes)
- All non-key attributes must depend directly on the primary key
</details>

## 3.2. Your ER Diagram

By defining your schema in **DBML**, your ERD should already be complete!

For some sanity checks, confirm your ERD includes:
- **Entities:** represented as rectangles with entity names
- **Attributes:** listed within each entity box
- **Primary keys:** clearly marked (underlined or highlighted)
- **Relationships:** shown as lines connecting entities
- **Cardinality:** indicated with appropriate symbols for 1:1, 1:N, N:1
- **Foreign keys:** clearly identified

## 3.3. 🧪 Validation

To check your schema for correctness, copy and past the your **DBML** definition into the `dbml/schema.dbml` file and run:

```bash
make test
```

<details>
<summary markdown='span'>❗ Troubleshooting</summary>

The tests are looking for tables named:
- `customers`
- `product`
- `orders`
- `order_items` - junction table linking `orders` and `products`

You may need to rename your tables
</details>

<br>

# 🏁 Finishing Up

By the end of this challenge, you have successfully done:
✅ **Data Analysis:** Deep understanding of the denormalized e-commerce dataset and identification of redundancy patterns
✅ **Conceptual Model:** Clear identification of 4 core business entities (`customers`, `products`, `orders`, `order_items`) and their high-level relationships
✅ **Logical Model:** Detailed normalized schema design following Third Normal Form principles, with proper primary and foreign key definitions
✅ **Professional ERD:** Visual representation of your database schema created as **DBML**, showing all entities, attributes, and relationships

Data modelling is essential for Data Engineers across both OLTP and OLAP systems. Understanding normalization principles allows you to make informed decisions about when to strategically denormalize for analytics performance. Well-designed schemas massively reduce storage costs, improve query efficiency, and are frequently tested in interviews.

Whether you're building ETL pipelines, designing data lakes, or implementing dimensional models, these foundational skills will make you more versatile as an engineer.

In the next challenge we'll look at implementing this schema into BigQuery with **SQL Data Definition Language (DDL)**!

🧪 To test all your code, run the following:

```bash
make test
```

And don't forget to push your code to Github to track your progress on Kitt!

<br>
