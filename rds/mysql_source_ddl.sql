CREATE TABLE dev.Product (
    productId VARCHAR(36) NOT NULL PRIMARY KEY,
    productName VARCHAR(255) NOT NULL,
    brandName VARCHAR(255),
    productDescription TEXT,
    price DECIMAL(10, 2) NOT NULL,
    productCategory VARCHAR(100)
);

#Customer Table
CREATE TABLE dev.Customer (
    customerId VARCHAR(36) NOT NULL PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    Address VARCHAR(255),
    Country VARCHAR(100),
    City VARCHAR(100)
);

 CREATE TABLE dev.Orders (
    orderId VARCHAR(36) NOT NULL PRIMARY KEY,
    orderCustomerId VARCHAR(36) NOT NULL,
    orderDate DATE NOT NULL,
    paymentMethod VARCHAR(50),
    orderPlatform VARCHAR(50),
    FOREIGN KEY (orderCustomerId) REFERENCES Customer(customerId)
);

CREATE TABLE dev.orderDetails (
    orderDetailsId VARCHAR(36) NOT NULL PRIMARY KEY,
    orderId VARCHAR(36) NOT NULL,
    productId VARCHAR(36) NOT NULL,
    Quantity INT NOT NULL,
    FOREIGN KEY (orderId) REFERENCES Orders(orderId),
    FOREIGN KEY (productId) REFERENCES Product(productId)
);

SET FOREIGN_KEY_CHECKS=0;






