# 🎯 Goal

**SCD Type 2** is the gold standard for data warehousing when you need to preserve complete historical records of dimensional changes. This approach creates new records for each change, enabling powerful temporal analytics and "point-in-time" reporting.

⚠️ **Important Note:** By implementing SCD Type 2, we will intentionally break the 3NF! This is a strategic denormalization - we're trading storage efficiency for analytical power. In data warehousing, this trade-off is often necessary to support business intelligence requirements that normalized OLTP designs cannot efficiently handle.

In this challenge, you will implement **SCD Type 2** patterns for customer segment evolution and master advanced temporal querying techniques. We will cover how to track customer lifecycle changes, analyze segment progression over time, and build production-ready dimensional tables that support sophisticated business intelligence.

**Why SCD Type 2 is Critical for Data Engineers:**
- **Historical Analytics**: Track customer segment evolution and lifecycle patterns
- **Business Intelligence**: Enable "point-in-time" analysis for any date in history
- **Customer Insights**: Analyze retention, churn, and upgrade behaviors over time
- **Advanced Analytics**: Support cohort analysis, trend reporting, and predictive modelling

The goal is to transform your customer table into a full-featured temporal dimension that preserves every segment change while supporting analytical queries.

<br>

# 0️⃣ Setup

Make sure to copy across your `.env` from the previous challenge, or make a copy of the `.env.sample` in this challenge and fill out the values.

Don't forget to load your environment variables!

<br>

# 1️⃣ SCD Type 2: Customer Segment Evolution 📊

**SCD Type 2** preserves historical changes by creating new records rather than overwriting existing ones. Unlike SCD Type 1 which overwrites data, Type 2 maintains a complete audit trail of every change, enabling powerful temporal analytics and business intelligence.

For customer analytics, SCD Type 2 is essential for tracking:
- **Customer segment progression** (Standard → Premium → VIP)
- **Customer value tier evolution** (Low Value → High Value)
- **Customer lifecycle analysis** and retention patterns
- **Point-in-time customer reporting** for any historical date

## 1.1. Understanding SCD Type 2 Structure

Your current customer table from the previous challenges has the foundation for SCD Type 2, but we need additional fields to track historical changes effectively.

**SCD Type 1 Challenges:**
- **Lost History**: Once you overwrite a customer's segment, you can't answer "How many Premium customers did we have in January 2018?"
- **No Trend Analysis**: Can't track customer lifecycle progression or identify upgrade/downgrade patterns
- **Limited Business Intelligence**: Can't perform cohort analysis or retention studies over time

**SCD Type 2 Solutions:**
- **Complete History**: Every segment change creates a new record
- **Point-in-Time Analysis**: Query customer state at any historical date
- **Trend Analysis**: Track customer journeys and lifecycle patterns
- **Business Intelligence**: Enable sophisticated customer analytics

To implement SCD Type 2, you will enhance your `customer` schema with additional tracking fields:

**Required SCD Type 2 Fields:**

<table>
  <thead>
    <tr>
      <th>Field Name</th>
      <th>Purpose</th>
      <th>Example</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><code>customer_key</code></td>
      <td><strong>Surrogate Key</strong> - Unique identifier for each version of a customer record</td>
      <td><code>cust_001_v1</code>, <code>cust_001_v2</code></td>
    </tr>
    <tr>
      <td><code>customer_id</code></td>
      <td><strong>Natural Key</strong> - Business identifier that remains constant across all versions</td>
      <td><code>ec2d2a258b058be...</code></td>
    </tr>
    <tr>
      <td><code>effective_date</code></td>
      <td><strong>Validity Start</strong> - When this version of the customer record became active</td>
      <td><code>2018-01-01 00:00:00</code></td>
    </tr>
    <tr>
      <td><code>end_date</code></td>
      <td><strong>Validity End</strong> - When this version expired (NULL = current record)</td>
      <td><code>2018-06-15 00:00:00</code> or <code>NULL</code></td>
    </tr>
    <tr>
      <td><code>is_current</code></td>
      <td><strong>Current Flag</strong> - Boolean flag for quick identification of active records</td>
      <td><code>TRUE</code> or <code>FALSE</code></td>
    </tr>
    <tr>
      <td><code>version_number</code></td>
      <td><strong>Version Control</strong> - Sequential number tracking record versions</td>
      <td><code>1</code>, <code>2</code>, <code>3</code></td>
    </tr>
  </tbody>
</table>

<br>

❓ Why do we need both `end_date` and `is_current`?
- **`end_date`**: Enables precise temporal queries ("customer state on 2018-03-15")
- **`is_current`**: Optimizes queries for current customer state (avoids NULL checks)
- **Both together**: Maximum query flexibility and performance

## 1.2. Create Customer SCD Type 2 Table

Now let's create an enhanced `customer` table with full SCD Type 2 support. This table will store multiple versions of each customer as their segments evolve over time.

❓ **Your Task**: Create a new SCD Type 2 enabled `customer` table named: `customers_scd2` that includes the additional required SCD Type 2 fields:
- All fields in the existing `customers` table
- `customer_key`
- `effective_date`
- `end_date`
- `is_current`

## 1.3. Load Initial Customer SCD Type 2 Data

Now we'll populate the SCD Type 2 table with initial customer data from your enhanced normalized `customers` table. Since this is the first load, all records will be marked as "current" with no end dates.

❓ **Your Task**: Populate the SCD Type 2 table with initial customer data.

💡 Hints:
1. Concat two existing fields together to generate your `customer_key`
2. Mark all records as current (`is_current = TRUE`, `end_date = NULL`)
3. Use existing `customer_segment_effective_date` as the starting point
4. Preserve existing version numbers from normalized table

🧪 After loading, verify your data with this query:

```sql
-- Verify initial SCD Type 2 load
SELECT
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_current = TRUE THEN 1 END) as current_records,
    COUNT(CASE WHEN end_date IS NULL THEN 1 END) as records_without_end_date,
    COUNT(DISTINCT customer_id) as unique_customers
FROM `olist_data_modelling.customers_scd2`;
```

**Expected Results**:
- `total_records` = `current_records` = `records_without_end_date` (all should be equal)
- `unique_customers` = number of distinct customers from your source table

<br>

# 2️⃣ Simulate Customer SCD Type 2 Changes 🔄

Now that your SCD Type 2 foundation is in place, let's simulate real customer lifecycle changes that require historical tracking. This is where SCD Type 2 shows its power - preserving every change while maintaining query performance.

## 2.1. Understanding SCD Type 2 Change Process

**SCD Type 2 Change Process (2-Step Pattern):**

1. **Close Current Record**: Set `end_date` and `is_current = FALSE` for the existing record
2. **Create New Record**: Insert new record with updated values and `is_current = TRUE`

This ensures:
- **No Data Loss**: Historical record is preserved
- **Clear Timeline**: Precise start/end dates for each version
- **Query Integrity**: Only one "current" record per customer at any time

## 2.2. Implementing Customer Segment Changes

Let's simulate real customer lifecycle changes that businesses need to track:

❓ **Your Task**: Implement customer segment upgrades using the SCD Type 2 pattern.

```sql
-- File: sql/simulate_customer_scd_changes.sql

-- ==================================================================
-- Scenario 1: Customer segment upgrade (Premium → VIP)
-- Business Context: Customer reaches spending threshold for VIP status
-- ==================================================================

-- Step 1: Close current record by setting end_date and is_current = FALSE
UPDATE `olist_data_modelling.customers_scd2`
SET
    end_date = TIMESTAMP('2018-06-15 10:00:00'),      -- Exact moment of change
    is_current = FALSE,                                -- No longer current
    record_last_updated = CURRENT_TIMESTAMP()         -- Audit trail
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028'
  AND is_current = TRUE;                               -- Only update current record

-- Step 2: Insert new record with upgraded segment
INSERT INTO `olist_data_modelling.customers_scd2`
SELECT
    -- New surrogate key with incremented version
    CONCAT(customer_id, '_v', CAST(version_number + 1 AS STRING)) as customer_key,

    -- Natural key remains the same
    customer_id,
    customer_unique_id,
    customer_name,
    customer_zip_code,

    -- *** CHANGED VALUES ***
    'VIP' as customer_segment,                         -- Upgraded from Premium
    'High Value' as customer_value_segment,            -- Upgraded value tier

    -- Unchanged attributes
    customer_since_date,

    -- SCD Type 2 fields for new record
    TIMESTAMP('2018-06-15 10:00:00') as effective_date, -- Same as previous end_date
    NULL as end_date,                                    -- New current record
    TRUE as is_current,                                  -- New current record
    version_number + 1,                                  -- Increment version

    -- Audit fields
    CURRENT_TIMESTAMP() as record_created_date,
    CURRENT_TIMESTAMP() as record_last_updated
FROM `olist_data_modelling.customers_scd2`
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028'
  AND version_number = (
    SELECT MAX(version_number)
    FROM `olist_data_modelling.customers_scd2`
    WHERE customer_id = 'ec2d2a258b058be97d409669ab436028'
  );
```

**Critical SCD Type 2 Rules:**

1. **Temporal Continuity**: New record's `effective_date` = old record's `end_date`
2. **Single Current Record**: Only one record per customer should have `is_current = TRUE`
3. **Version Sequencing**: Version numbers should increment sequentially
4. **Natural Key Consistency**: `customer_id` remains constant across all versions
5. **Surrogate Key Uniqueness**: Each record gets a unique `customer_key`

## 2.3. Verifying SCD Type 2 Changes

❓ **Your Task**: Verify the customer segment change was implemented correctly:

```sql
-- Verify the customer segment upgrade
SELECT
    customer_key,
    customer_id,
    customer_segment,
    customer_value_segment,
    effective_date,
    end_date,
    is_current,
    version_number
FROM `olist_data_modelling.customers_scd2`
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028'
ORDER BY version_number;
```

**Expected Results:**
- **Version 1**: `Premium` → `FALSE` (is_current) → `2018-06-15 10:00:00` (end_date)
- **Version 2**: `VIP` → `TRUE` (is_current) → `NULL` (end_date)
- **Timeline**: No gaps or overlaps in effective/end dates

<details>
<summary markdown='span'>💡 SCD Type 2 Implementation Best Practices</summary>

**Query Performance Tips:**
```sql
-- Always use is_current flag for current state queries
SELECT * FROM customers_scd2 WHERE is_current = TRUE;

-- Use effective_date/end_date for point-in-time queries
SELECT * FROM customers_scd2
WHERE effective_date <= @target_date
  AND (end_date IS NULL OR end_date > @target_date);
```

**Data Quality Checks:**
```sql
-- Verify no customer has multiple current records
SELECT customer_id, COUNT(*) as current_count
FROM customers_scd2
WHERE is_current = TRUE
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- Check for temporal gaps or overlaps
WITH customer_timeline AS (
  SELECT customer_id, effective_date, end_date,
    LEAD(effective_date) OVER (
      PARTITION BY customer_id ORDER BY version_number
    ) as next_effective_date
  FROM customers_scd2
  WHERE end_date IS NOT NULL
)
SELECT * FROM customer_timeline
WHERE end_date != next_effective_date;
```

**Common Pitfalls to Avoid:**
- Forgetting to close current records before inserting new ones
- Creating temporal gaps or overlaps in effective/end dates
- Not incrementing version numbers properly
- Using wrong customer for surrogate key generation
- Forgetting to update audit fields
</details>

<br>

# 3️⃣ Practice SCD Type 2 Exercise 📈

Implement one more customer segment change to reinforce the 2-step process, choose any appropriate customer:

❓ **Scenario: Customer Downgrade (VIP → Premium)**
- Business Context: a customer's spending dropped below VIP threshold.
- Customer: Choose a different customer_id from your table
- Change Date: 2018-08-20 14:30:00
- New Segment: Premium → Medium Value

💡 Follow the same process:
1. Close the current record
2. Insert new record with downgraded segment


🧪 **Verification**: After implementing, run a query to see both versions of your chosen customer and verify the timeline is correct.

<br>

# 4️⃣ SCD Type 2 vs Type 1 Benefits 🔍

Now let's see the power of SCD Type 2 by comparing what's possible versus your original normalized table.

## 4.1. Historical State Preservation

**With SCD Type 2 - Complete History:**
```sql
-- See all versions of a customer over time
SELECT
    customer_id,
    customer_segment,
    effective_date,
    end_date,
    is_current,
    version_number
FROM `olist_data_modelling.customers_scd2`
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028'
ORDER BY version_number;
```

**With SCD Type 1 - Lost History:**
```sql
-- Only see current state
SELECT
    customer_id,
    customer_segment,
    record_last_updated
FROM `olist_data_modelling.customers`
WHERE customer_id = 'ec2d2a258b058be97d409669ab436028';
```

## 4.2. Point-in-Time Analysis

**SCD Type 2 enables questions like:**
- "How many VIP customers did we have on June 1st, 2018?"
- "Show me the customer segment distribution as of any historical date"
- "Which customers have changed segments and when?"

```sql
-- Point-in-time customer segments (e.g., June 1st, 2018)
SELECT
    customer_segment,
    COUNT(*) as customer_count
FROM `olist_data_modelling.customers_scd2`
WHERE effective_date <= TIMESTAMP('2018-06-01 00:00:00')
  AND (end_date IS NULL OR end_date > TIMESTAMP('2018-06-01 00:00:00'))
GROUP BY customer_segment
ORDER BY customer_count DESC;
```

**SCD Type 1 cannot answer these questions** - the historical data is gone forever.

## 4.3. Customer Journey Tracking

**With SCD Type 2 - Track Complete Journeys:**
```sql
-- See customers who have changed segments
SELECT
    customer_id,
    COUNT(*) - 1 as total_changes,
    MIN(effective_date) as first_segment_date,
    MAX(effective_date) as latest_change_date
FROM `olist_data_modelling.customers_scd2`
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY total_changes DESC;
```

**With SCD Type 1:** No way to track customer progression or identify upgrade patterns.

# 🏁 Finishing Up

Congratulations! You have successfully implemented SCD Type 2 and experienced its power for preserving historical data.

**What you accomplished:**
- ✅ Created temporal dimensions with complete historical audit trails
- ✅ Mastered the 2-step change process (close current → create new)
- ✅ Demonstrated historical preservation vs. data loss in SCD Type 1

**The SCD Type 2 Advantage:**

**✅ What you gain with SCD Type 2:**
- Complete audit trail of all changes
- Point-in-time analysis capabilities ("How many VIP customers on June 1st?")
- Customer lifecycle and journey tracking
- Ability to "time travel" to any historical date

**❌ What you lose with SCD Type 1:**
- All historical context disappears forever
- Cannot track customer evolution or upgrade patterns
- Limited business intelligence capabilities

**Your Journey**: From simple normalized tables → production-ready temporal dimensions that enable sophisticated business intelligence.

These SCD Type 2 patterns are fundamental for modern data warehousing and frequently tested in data engineering interviews.

🧪 Test your SCD Type 2 schema and process with:

```bash
make test
```

Don't forget to push your code to Github to track your progress on Kitt!

<br>
