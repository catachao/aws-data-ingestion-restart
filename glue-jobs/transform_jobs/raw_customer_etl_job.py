"""%%configure 
{
  "--job-bookmark-option": "job-bookmark-enable"
} """   

import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext	
from pyspark.sql.functions import current_timestamp, lit, sha2, concat_ws, col, current_date, split
from pyspark.sql.types import TimestampType
from awsglue.dynamicframe import DynamicFrame
from awsglue.utils import getResolvedOptions
from awsglue.job import Job

#Initialize all the variables needed
source_bucket = "data-engineering-project-953333998402"
folder_name = "bronze_data"
processed_folder_name = "silver_data"
db_name = "dev"
table_name = "Customer"

# Set up catalog parameters
glue_database = "data-engineering-project-glue-database"
glue_table_name = "raw_data_customer"

#set up the spark contexts, glue contexts and initialize job
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)  
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
job.init(args['JOB_NAME'], args)


#Read data from data catalog
customer_df_from_catalog = glueContext.create_data_frame_from_catalog(glue_database,\
                            glue_table_name,additional_options = {"useCatalogSchema": True, "useSparkDataSource": True, "header":True},\
                                transformation_ctx = "customer_df_from_catalog")

# Check if the DataFrame has records before processing
if customer_df_from_catalog.count() > 0:
    
    #Create new dataframe for renamed fields
    renamed_customer = customer_df_from_catalog.withColumnRenamed("customerid","customer_id")\
                        .withColumnRenamed("op", "cdc_operation")\
                        .withColumnRenamed("phone","cust_phone")\
                        .withColumnRenamed("address","cust_address")\
                        .withColumnRenamed("country","cust_country")\
                        .withColumnRenamed("city","cust_city")\
                        .withColumnRenamed("email", "cust_email")\
                        .withColumnRenamed("name", "cust_name")\


    #Create new default values and timestamp
    current_ts = current_timestamp()
    current_date = current_date()
    record_end_ts = lit('9999-12-31').cast(TimestampType())
    active_flag = lit(1)

    #concatenate changing columns to create hash value
    concatenated_customer_fields = concat_ws(''\
                                        , col("cust_phone")\
                                        , col("cust_address")\
                                        , col("cust_country")\
                                        , col("cust_city")\
                                        , col("cust_name"))
    #create dataframe with new columns 
    customer_final_df = renamed_customer.withColumn("hash_value",sha2(concatenated_customer_fields, 256))\
                        .withColumn("record_start_ts",current_ts)\
                        .withColumn("record_end_ts",record_end_ts)\
                        .withColumn("ingestion_date", current_date)\
                        .withColumn("active_flag",active_flag)\
                        .withColumn("cust_first_name", split(renamed_customer["cust_name"], " ")[0])\
                        .withColumn("cust_last_name", split(renamed_customer["cust_name"], " ")[1])\
                        .drop("cust_name")\

    #create glue dynamicframe from the dataframe
    customer_final_dyf = DynamicFrame.fromDF(customer_final_df,glueContext,"customer_final_dyf")  

    #Write rows to S3 as Parquet
    glueContext.write_dynamic_frame.from_options(
        frame = customer_final_dyf,
        connection_type = "s3",    
        connection_options = {"path": f"s3://{source_bucket}/{processed_folder_name}/{db_name}/{table_name}/", "partitionKeys": ["ingestion_date"]},
        format = "parquet",
        transformation_ctx = "customer_dyf_to_S3"
    )

else:
    print("No new records found in the source data. Skipping further processing.")
    
job.commit()