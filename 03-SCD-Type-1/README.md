# 🎯 Goal

**SCD Type 1 (Slowly Changing Dimensions)** is a fundamental data warehousing pattern that handles dimensional data changes by **overwriting** old values with new ones. This approach is perfect for corrections, standardizations, and changes where historical values aren't important for business analysis.

In this challenge, you will enhance your normalized tables with **production-ready audit fields** and implement **SCD Type 1** patterns for customer data management. You'll learn when overwriting data is appropriate and practice handling real-world scenarios like address changes and data quality corrections.

**Why SCD Type 1 Matters for Data Engineers:**
- **Data Quality**: Handle corrections and standardizations efficiently
- **Storage Optimization**: Minimize storage overhead when history isn't needed
- **Performance**: Faster queries when you only need current state
- **Production Readiness**: Transform schemas into enterprise-grade systems

The goal is to evolve your customer table from a simple normalized structure to a production-ready dimension with audit trails and temporal awareness.

### Contextual Disclaimer

Our data is transactional data in 3NF, and hasn't been _intentionally denormalised_ for an analytics use case, we are still very much working in a transactional context.

In the following unit, **Data Warehousing**, we'll explore how analytical data stores can be designed. This unit is focussing on the technical implementations of 3NF and SCDs.

<br>

# 0️⃣ Setup

Make sure to copy across your `.env` from the previous challenge, or make a copy of the `.env.sample` in this challenge and fill out the values.

Don't forget to load your environment variables with:

```bash
direnv reload
```

<br>

# 1️⃣ Temporal Ready Schema Enhancement 🔧

Your normalized tables work great for basic analytics, but **production data warehouses** require additional capabilities for tracking changes over time, debugging data issues, and maintaining audit trails. The idea is to add the three audit fields from the original, denormalised, raw data:
- `record_created_date`
- `record_last_updated`
- `data_version`

To every table. Does it feel like there is data duplication happening here? Yes, but there is not an easy way around this, and it will still be more space efficient than the large, denormalized mega table, while allowing for tracking changes as a function of time.

Let's enhance your static schema with **production-ready audit fields**! 🚀

## 1.1. Understanding Audit Fields

❓ **Discussion**: Why do production data systems need these fields?

**Audit fields provide:**
- **Data Lineage**: When was this record created? When was it last updated?
- **Version Control**: How many times has this record changed?
- **Debugging**: Track data quality issues back to specific load processes
- **Compliance**: Audit trails for financial, healthcare, and other highly regulated domains

## 1.2. Enhance Your Tables with Audit Fields

You'll need to enhance your existing table schema to account for the new columns. Schema change and evolution over time is normal and expected as business needs change. Luckily for us, the syntax for adding a new column to a table schema in BigQuery is relatively straight forward with an `ALTER TABLE` statement:

```sql
ALTER TABLE `my_dataset.my_table`
ADD COLUMN my_new_column_name TIMESTAMP,
ADD COLUMN my_other_new_column_name INT64;
```

❓ **Your Task**: Add audit columns to your normalized tables to make them production-ready. You will need to create a separate `ALTER TABLE` for each table. Create a SQL script in the `sql/` directory named: `add_audit_columns.sql` with your **ALTER TABLE** queries.

Run your DDL queries in the BigQuery console as a SQL script, either one at a time or all together. Alternatively use the `bq` CLI tool to execute SQL scripts:

```bash
bq query --use_legacy_sql=false < path/to/sql_script.sql
```

Make sure to look at the changed schema and the data in the BigQuery console to make sure your tables have been altered!

## 1.3. Populate Audit Fields from Source Data

You have the fields for the table, now populate these fields with data from your original denormalized source. You can achieve this with an **UPDATE** query. An example query for the `customers` table:

```sql
-- Update customers audit fields
UPDATE `olist_data_modelling.customers` customers
SET
  record_created_date = source.record_created_date,
  record_last_updated = source.record_last_updated,
  data_version = source.data_version
FROM (
  SELECT DISTINCT
    customer_id,
    record_created_date,
    record_last_updated,
    data_version
  FROM `olist_data_modelling.raw_sales_transactions`
) AS source
WHERE customers.customer_id = source.customer_id;
```

❓ In the `sql/` directory, create a file called `insert_audit_field_data.sql` and create your **UPDATE** queries for all the tables: `customers`, `orders`, `products`, `order_items`.

💡 Your update script for `order_items` will be different from `customers`, `orders`, and `products`. Refer to your initial SQL scripts that you used to insert data into your normalised tables, they will follow the same pattern as these update scripts.

Run your DDL queries in the BigQuery console as a SQL script, either one at a time or all together. Alternatively use the `bq` CLI tool to execute SQL scripts:

```bash
bq query --use_legacy_sql=false < path/to/sql_script.sql
```

## 1.4. Verify Your Enhanced Schema

🧪 **Validation**: Check that audit fields are properly populated.

```bash
bq query --use_legacy_sql=false < sql/verify_updated_schema.sql
```

🎯 **Expected Result**: All counts should match for each table (no NULL audit fields).

🧪 Alternatively test with:

```bash
make test
```

<br>

# 2️⃣ Understanding Customer Temporal Data 🕐

Now that your tables are temporal-ready, let's think about the temporal aspects of your **customer data** to understand what changes over time and why it matters for business analytics.

## 2.1. Customer Temporal Analysis and Business Scenarios

❓ **Discussion**: Consider these real-world customer analytics scenarios and questions - you **do not** have to definitively answer them:

**Business Questions Requiring Temporal Data:**
1. **"How many customers were in the Premium segment on January 1st, 2018?"**
2. **"Which customers upgraded from Standard to Premium segment and when?"**
3. **"What's the average time customers spend in each segment before upgrading?"**
4. **"How has customer acquisition evolved by segment over time?"**
5. **"Which customers have been with us the longest but never upgraded segments?"**

❓ **Critical Thinking Questions**:
- Looking at your customer table, which attributes would change frequently vs. rarely?
- What business events might trigger customer segment upgrades?
- How would you handle a customer's address change vs. segment change differently?
- Why might you need historical customer segment data for marketing campaigns?
- Which customer changes are corrections vs. true business events?
- What customer attributes would marketing teams want to analyze over time?

## 2.2. Identifying Change Types

Let's categorize customer attributes by how they should be handled:

**Type 1 Candidates (Overwrite - History Not Important):**
- `customer_zip_code` (address changes)
- `customer_name` (standardization, corrections)

**Type 2 Candidates (Track History - Business Critical):**
- `customer_segment` (Standard, Premium, VIP)
- `customer_value_segment` (Low Value, Medium Value, High Value)
- `customer_segment_effective_date` (when segment became active)

<br>

# 3️⃣ SCD Type 1: Customer Address Updates 🔄

**SCD Type 1** overwrites old values with new ones. For customers, this is perfect for:
- Address changes (customers move)
- Contact information updates
- Data corrections and standardization

## 3.1. Implementing Customer SCD Type 1

Let's simulate a customer moving to a new address using SCD Type 1:

❓ **Your Task**: Create procedures to handle customer address changes.

```sql
-- File: sql/customer_scd_type1_updates.sql

-- Scenario 1: Customer moving to a new address (SCD Type 1)
UPDATE `olist_data_modelling.customers`
SET
    customer_zip_code = 22070900,
    record_last_updated = CURRENT_TIMESTAMP(),
    data_version = data_version + 1        -- Increment version
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028';

-- Verify the change
SELECT
    customer_id,
    customer_name,
    customer_zip_code,
    customer_segment,
    record_last_updated,
    data_version
FROM `olist_data_modelling.customers`
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028';
```

## 3.2. Customer SCD Type 1 Exercises

❓ **Practice Exercises**: Write SCD Type 1 updates for these customer scenarios:

1. **Customer Name Standardization**:
   - Change "Customer_ec2d2a25" to "Customer EC2D2A25"
   - Update multiple customers to follow consistent naming pattern

2. **Address Correction**:
   - A customer's ZIP code was incorrectly entered as 2878, should be 28780
   - Fix the data quality issue using SCD Type 1

<details>
<summary markdown='span'>💡 When to Use SCD Type 1</summary>

**Good for SCD Type 1:**
- Customer contact information (address, phone, email)
- Product specifications corrections (weight, dimensions)
- Data standardization and clean up
- Reference data that doesn't require history

**Avoid SCD Type 1 for:**
- Business-critical changes (customer segment, product pricing)
- Regulatory data requiring audit trails
- Changes used for trend analysis
</details>

<br>

# 🏁 Finishing Up

Congratulations! You have successfully implemented SCD Type 1 and enhanced your normalized tables with production-ready audit capabilities.

**Key Accomplishments:**
- ✅ Enhanced academic tables with audit fields for enterprise use
- ✅ Implemented SCD Type 1 patterns for customer data management
- ✅ Learned when to overwrite data vs. preserve history
- ✅ Practised real-world data quality and standardization scenarios

Your customer table has evolved from a simple normalized structure to a production-ready dimension with temporal awareness. These SCD Type 1 skills are essential for data quality operations, compliance tracking, and efficient updates when historical values aren't needed.

**Next Steps:** These patterns prepare you for SCD Type 2, where you'll learn to preserve complete historical records for business-critical changes like customer segment evolution.

🧪 Test your updated SCD Type 1 Schema, run:

```bash
make test
```
And don't forget to push your code to Github to track your progress on Kitt!

<br>
