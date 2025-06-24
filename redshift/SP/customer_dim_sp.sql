CREATE OR REPLACE PROCEDURE sales.sp_merge_dim_customer()
 LANGUAGE plpgsql
AS $$
BEGIN

-- Upwomer for all U and D records from the deduplicated table
UPDATE sales.dim_customer
SET record_end_ts = b.record_start_ts - interval '1 second', 
    active_flag = 0
FROM (
    WITH deduped_stage AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY record_start_ts DESC) AS row_num
        FROM sales.stage_dim_customer
    )
    SELECT *
    FROM deduped_stage
    WHERE row_num = 1
) b
WHERE sales.dim_customer.customer_id = b.customer_id
AND sales.dim_customer.record_end_ts > b.record_start_ts
AND sales.dim_customer.active_flag = 1
AND (b.cdc_operation = 'U' OR b.cdc_operation = 'D');

-- Insert records into dim_customer for all I and U records from the deduplicated table
INSERT INTO sales.dim_customer
   (cdc_operation, customer_id, cust_email, cust_phone, cust_address, cust_country, 
    cust_city, hash_value, record_start_ts, record_end_ts, 
    active_flag, cust_first_name, cust_last_name) 
SELECT
    b.cdc_operation, b.customer_id, b.cust_email, b.cust_phone, b.cust_address, 
    b.cust_country, b.cust_city, b.hash_value, 
    b.record_start_ts, b.record_end_ts, b.active_flag, b.cust_first_name, 
    b.cust_last_name
FROM (
    WITH deduped_stage AS (
        SELECT *,
               ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY record_start_ts DESC) AS row_num
        FROM sales.stage_dim_customer
    )
    SELECT *
    FROM deduped_stage
    WHERE row_num = 1
) b
WHERE b.cdc_operation = 'U' OR b.cdc_operation = 'I';

-- Truncate the staging table
TRUNCATE TABLE sales.stage_dim_customer;

END;
$$


	
