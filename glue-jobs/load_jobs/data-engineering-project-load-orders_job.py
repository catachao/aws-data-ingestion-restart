# data-engineering-project-load-orders_job

import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node Amazon S3
AmazonS3_node1750406517522 = glueContext.create_dynamic_frame.from_options(format_options={}, connection_type="s3", format="parquet", connection_options={"paths": ["s3://data-engineering-project-953333998402/silver_data/dev/Orders/"], "recurse": True}, transformation_ctx="AmazonS3_node1750406517522")

# Script generated for node Amazon Redshift
AmazonRedshift_node1750406541199 = glueContext.write_dynamic_frame.from_options(frame=AmazonS3_node1750406517522, connection_type="redshift", connection_options={"redshiftTmpDir": "s3://aws-glue-assets-953333998402-us-east-2/temporary/", "useConnectionProperties": "true", "dbtable": "sales.fact_orders", "connectionName": "Redshift connection", "preactions": "CREATE TABLE IF NOT EXISTS sales.fact_orders (order_id_ VARCHAR, order_customer_id VARCHAR, order_date DATE, payment_method VARCHAR, order_platform VARCHAR, order_year INTEGER, order_month INTEGER, ingestion_date DATE);"}, transformation_ctx="AmazonRedshift_node1750406541199")

job.commit()