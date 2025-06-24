-------------------------------->
--Create Orders Fact Table
CREATE TABLE sales.fact_orders (
    order_id_ character varying(64) NOT NULL ENCODE lzo,
    order_customer_id character varying(64) ENCODE lzo,
    order_date date ENCODE az64,
    order_status character varying(64) ENCODE lzo,
    payment_method character varying(64) ENCODE lzo,
    order_platform character varying(64) ENCODE lzo,
    order_year integer ENCODE az64,
    order_month integer ENCODE az64,
    ingestion_date date ENCODE az64,
    PRIMARY KEY (order_id_)
)   DISTSTYLE AUTO
    SORTKEY AUTO;

-------------------------------->


