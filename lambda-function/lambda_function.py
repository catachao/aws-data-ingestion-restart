import mysql.connector
from mysql.connector import Error
import random
import uuid
from datetime import datetime
import boto3
import json
import base64
from botocore.exceptions import ClientError
from faker import Faker
import os
import re
from datetime import timedelta


# Initialize Faker
fake = Faker()

# Map countries to cities
country_city_mapping = {
    'UK': ['London', 'Manchester', 'Birmingham', 'Leeds'],
}

# Get database credentials from AWS Secrets Manager
def get_db_credentials():
    secret_name = os.getenv("SECRET_NAME")  # Get secret name from environment variable
    region_name = os.getenv("REGION_NAME")  # Get region name from environment variable
    
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

        return json.loads(secret)
    except ClientError as e:
        print(f"Error retrieving secret from Secrets Manager: {e}")
        raise e

# Create a connection to MySQL (Amazon RDS)
def create_connection():
    # Get the database credentials from Secrets Manager
    db_credentials = get_db_credentials()

    try:
        connection = mysql.connector.connect(
            host=db_credentials["host"],
            user=db_credentials["username"],
            password=db_credentials["password"],
            database=db_credentials["dbname"]
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Insert products
def insert_products(cursor, num_products):
    for _ in range(num_products):
        productId = str(uuid.uuid4())
        productName = fake.word().capitalize()
        brandName = random.choices(['Urban Nomad', 'Coastal', 'Threads', 'Silver & Stitch', 'Lilo'],weights = [10, 10, 40, 30, 10])[0]
        print(brandName)
        productDescription = fake.sentence()
        price = round(random.uniform(10, 100), 2)
        productCategory = random.choices(['Jewelry', 'Bags', 'Clothing', 'Swimwear', 'Shoes'], weights = [20, 10, 40, 20, 10])[0]

        insert_query = """INSERT INTO Product (productId, productName, brandName, productDescription, price, productCategory)
                          VALUES (%s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (productId, productName, brandName, productDescription, price, productCategory))


# Insert customers
def insert_customers(cursor, num_customers):
    for _ in range(num_customers):
        customerId = str(uuid.uuid4())
        Name = fake.name()
        # Convert name to lowercase and remove spaces or special characters to create an email
        formatted_name = re.sub(r'[^a-zA-Z]', '', Name.lower())
        Email = f"{formatted_name}@email.com"
        Phone = fake.phone_number()
        Address = fake.street_address()
        Country = random.choice(list(country_city_mapping.keys()))
        City = random.choices(country_city_mapping[Country], weights = [ 60, 20, 10, 10])[0]

        insert_query = """INSERT INTO Customer (customerId, Name, Email, Phone, Address, Country, City)
                          VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(insert_query, (customerId, Name, Email, Phone, Address, Country, City))

# Update customer data
def update_customers(cursor):
    cursor.execute("SELECT customerId FROM Customer")
    customer_ids = [row[0] for row in cursor.fetchall()]

    if customer_ids:
        customerId = random.choice(customer_ids)
        new_email = fake.email()
        new_phone = fake.phone_number()

        update_query = """UPDATE Customer
                          SET Email = %s, Phone = %s
                          WHERE customerId = %s"""
        cursor.execute(update_query, (new_email, new_phone, customerId))

# Delete customer data
def delete_customers(cursor):
    cursor.execute("SELECT customerId FROM Customer")
    customer_ids = [row[0] for row in cursor.fetchall()]

    if customer_ids:
        customerId = random.choice(customer_ids)
        delete_query = """DELETE FROM Customer WHERE customerId = %s"""
        cursor.execute(delete_query, (customerId,))


def insert_orders_and_order_details(cursor, num_orders):
    cursor.execute("SELECT productId FROM Product")
    product_ids = [row[0] for row in cursor.fetchall()]

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    total_days = (end_date - start_date).days

    cursor.execute("SELECT customerId FROM Customer")
    customer_ids = [row[0] for row in cursor.fetchall()]

    for _ in range(num_orders):
        # Create order
        orderId = str(uuid.uuid4())
        orderCustomerId = random.choice(customer_ids)

        random_days = random.randint(0, total_days)
        orderDate = datetime.now().strftime("%Y-%m-%d")  # Set to current date

        paymentMethod = random.choices(['Credit Card', 'PayPal', 'Bank Transfer'], weights = [80, 15, 5])[0]
        orderPlatform = random.choices(['Website', 'Mobile', 'In-store'], weights = [50, 30, 20])[0]

        insert_order_query = """INSERT INTO Orders (orderId, orderCustomerId, orderDate, paymentMethod, orderPlatform)
                                VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(insert_order_query, (orderId, orderCustomerId, orderDate, paymentMethod, orderPlatform))

        # Insert corresponding order details for the created order
        num_order_details = random.randint(1, 5)  # Random number of order details per order
        for _ in range(num_order_details):
            orderDetailsId = str(uuid.uuid4())
            productId = random.choice(product_ids)
            Quantity = random.randint(1, 5)

            insert_order_details_query = """INSERT INTO orderDetails (orderDetailsId, orderId, productId, Quantity)
                                            VALUES (%s, %s, %s, %s)"""
            cursor.execute(insert_order_details_query, (orderDetailsId, orderId, productId, Quantity))



# Main lambda handler function
def lambda_handler(event, context):
    connection = create_connection()
    if connection is not None:
        cursor = connection.cursor()
        try:
            connection.autocommit = False

            # Insert products 
            insert_products(cursor, random.randint(1, 2))

            # Insert customers 
            insert_customers(cursor,random.randint(1, 3))

            # Insert orders and their corresponding order details
            insert_orders_and_order_details(cursor, random.randint(5, 15))


            # Occasionally update and delete customer data
            if random.random() < 0.5:  # 50% chance to update customers
                update_customers(cursor)
            if random.random() < 0.2:  # 20% chance to delete customers
                delete_customers(cursor)

            connection.commit()
            return {
                'statusCode': 200,
                'body': 'Data successfully inserted, updated, and/or deleted in the database'
            }
        except Error as e:
            print(f"Error while inserting data: {e}")
            connection.rollback()
            return {
                'statusCode': 500,
                'body': f"Error occurred: {e}"
            }
        finally:
            cursor.close()
            connection.close()
            print("Connection closed")
    else:
        return {
            'statusCode': 500,
            'body': 'Failed to connect to the database'
        }

