"""%%configure 
{
  "--job-bookmark-option": "job-bookmark-enable"
} """       

import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext	
from pyspark.sql.functions import current_timestamp, lit, sha2, concat_ws, col, current_date, split,to_date, round, year, month
from pyspark.sql.types import TimestampType, DateType
from awsglue.dynamicframe import DynamicFrame
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

#Initialize all the variables needed
source_bucket = "data-engineering-905418446260"
folder_name = "bronze_data"
processed_folder_name = "silver_data"
db_name = "dev"
table_name = "orderDetails"

# Set up catalog parameters
glue_database = "dataeng-glue-database"
glue_table_name = "raw_data_orderdetails"

#set up the spark contexts, glue contexts and initialize job
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)  
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
job.init(args['JOB_NAME'], args)

#Read data from data catalog
order_details_df_from_catalog = glueContext.create_data_frame_from_catalog(glue_database,\
                            glue_table_name,additional_options = {"useCatalogSchema": True},\
                                transformation_ctx = "orderdetails_df_from_catalog")

if order_details_df_from_catalog.count() > 0: 
    #Create new dataframe for renamed fields
    renamed_order_details = order_details_df_from_catalog.withColumnRenamed("orderDetailsId","order_details_id ")\
                        .withColumnRenamed("orderId","order_id")\
                        .withColumnRenamed("productid","product_id")\
                        .withColumnRenamed("Quantity","product_quantity")\
                        .drop("op")
    
    #Create current_date variable
    current_date = current_date()

    #create dataframe with new columns using withColumn()
    order_details_final_df = renamed_order_details.withColumn("ingestion_date",current_date)\
                                .withColumn("ingestion_date_pk",current_date)

    order_details_final_dyf = DynamicFrame.fromDF(order_details_final_df,glueContext,"product_final_dyf")  

    #Write rows to S3 as Parquet
    glueContext.write_dynamic_frame.from_options(
        frame = order_details_final_dyf,
        connection_type = "s3",    
        connection_options = {"path": f"s3://{source_bucket}/{processed_folder_name}/{db_name}/{table_name}/", "partitionKeys": ["ingestion_date_pk"]},
        format = "parquet",
        transformation_ctx = "order_details_final_dyf"
    )
    
else:
    print("No new records found in the source data. Skipping further processing.")

job.commit()