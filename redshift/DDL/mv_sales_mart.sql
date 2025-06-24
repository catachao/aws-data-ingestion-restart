-- MV Sales summary data mart
CREATE MATERIALIZED VIEW sales.mv_sales_mart 
AUTO REFRESH YES
AS
SELECT
    fo.order_id_,
    fo.order_date,
    fo.payment_method,
    fo.order_platform,
    fo.order_month,
    fo.order_year,
    fod.order_details_id_,
    fod.product_quantity,
    dp.product_name,
    dp.brand_name,
    dp.product_category,
    (dp.product_price * fod.product_quantity) AS total_revenue,
    dc.customer_id,
    dc.cust_city,
    dc.cust_country
FROM
    sales.fact_orders fo
    JOIN sales.fact_order_details fod ON fo.order_id_ = fod.order_id
    JOIN sales.dim_product dp ON fod.product_id = dp.product_id 
    JOIN sales.dim_customer dc ON fo.order_customer_id = dc.customer_id



