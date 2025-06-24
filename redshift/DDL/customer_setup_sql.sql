
-------------------------------->
--Create Customer Dimension Table
CREATE TABLE sales.dim_customer (
    cdc_operation character varying(50) ENCODE lzo,
    customer_id character varying(64) NOT NULL ENCODE lzo
    distkey
,
        cust_email character varying(64) ENCODE lzo,
        cust_phone character varying(64) ENCODE lzo,
        cust_address character varying(65535) ENCODE lzo,
        cust_country character varying(64) ENCODE lzo,
        cust_city character varying(64) ENCODE lzo,
        hash_value character varying(64) ENCODE lzo,
        record_start_ts timestamp without time zone ENCODE az64,
        record_end_ts timestamp without time zone ENCODE az64,
        active_flag integer ENCODE az64,
        cust_first_name character varying(64) ENCODE lzo,
        cust_last_name character varying(64) ENCODE lzo,
        PRIMARY KEY (customer_id)
) DISTSTYLE KEY;

-------------------------------->
---Create Customer staging table

CREATE TABLE sales.stage_dim_customer (
    cdc_operation character varying(50) ENCODE lzo,
    customer_id character varying(64) NOT NULL ENCODE lzo
    distkey
,
        cust_email character varying(64) ENCODE lzo,
        cust_phone character varying(64) ENCODE lzo,
        cust_address character varying(65535) ENCODE lzo,
        cust_country character varying(64) ENCODE lzo,
        cust_city character varying(64) ENCODE lzo,
        hash_value character varying(64) ENCODE lzo,
        record_start_ts timestamp without time zone ENCODE az64,
        record_end_ts timestamp without time zone ENCODE az64,
        active_flag integer ENCODE az64,
        cust_first_name character varying(64) ENCODE lzo,
        cust_last_name character varying(64) ENCODE lzo,
        PRIMARY KEY (customer_id)
) BACKUP NO DISTSTYLE KEY;

