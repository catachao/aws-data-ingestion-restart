-------------------------------->

--Create Order Details Fact Table
CREATE TABLE sales.fact_order_details (
    order_details_id_ character varying(64) NOT NULL ENCODE lzo,
    order_id character varying(64) ENCODE lzo,
    product_id character varying(64) ENCODE lzo,
    product_quantity bigint ENCODE az64,
    ingestion_date date ENCODE az64,
    PRIMARY KEY (order_details_id_)
)
    DISTSTYLE AUTO
    SORTKEY AUTO;
-------------------------------->

