-- Virtual Try-On E-Commerce Database Schema
-- Run this in MySQL Workbench to create the database

CREATE DATABASE IF NOT EXISTS virtual_tryon_db;
USE virtual_tryon_db;

-- Users table for authentication
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    postal_code VARCHAR(10),
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Body measurements table for size estimation
CREATE TABLE IF NOT EXISTS user_measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    height_cm DECIMAL(5,2),
    weight_kg DECIMAL(5,2),
    chest_cm DECIMAL(5,2),
    waist_cm DECIMAL(5,2),
    shoulder_cm DECIMAL(5,2),
    arm_length_cm DECIMAL(5,2),
    estimated_size VARCHAR(5), -- S, M, L, XL, XXL
    measured_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Products (Garments) table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    garment_id VARCHAR(50) UNIQUE NOT NULL, -- jin_17, lab_03, etc.
    product_name VARCHAR(100) NOT NULL,
    brand VARCHAR(100),
    category VARCHAR(50), -- Jacket, Lab Coat, Shirt, etc.
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    discount_percent DECIMAL(5,2) DEFAULT 0,
    image_path VARCHAR(255),
    model_available BOOLEAN DEFAULT TRUE, -- Has trained model
    in_stock BOOLEAN DEFAULT TRUE,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_garment_id (garment_id),
    INDEX idx_category (category)
);

-- Product sizes and availability
CREATE TABLE IF NOT EXISTS product_sizes (
    size_id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    size VARCHAR(5) NOT NULL, -- S, M, L, XL, XXL
    stock_quantity INT DEFAULT 0,
    available BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_product_size (product_id, size),
    INDEX idx_product_id (product_id)
);

-- Shopping cart
CREATE TABLE IF NOT EXISTS cart (
    cart_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    size VARCHAR(5) NOT NULL,
    quantity INT DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product_size (user_id, product_id, size),
    INDEX idx_user_id (user_id)
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    order_status ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled') DEFAULT 'pending',
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    payment_method VARCHAR(50),
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_order_number (order_number)
);

-- Order items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    size VARCHAR(5) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id)
);

-- Virtual closet - saved outfits and preferences
CREATE TABLE IF NOT EXISTS virtual_closet (
    closet_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    tried_on BOOLEAN DEFAULT FALSE,
    favorited BOOLEAN DEFAULT FALSE,
    notes TEXT,
    tried_at TIMESTAMP NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_favorited (favorited)
);

-- Virtual try-on sessions for tracking
CREATE TABLE IF NOT EXISTS tryon_sessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    estimated_size VARCHAR(5),
    session_duration INT, -- seconds
    saved_to_closet BOOLEAN DEFAULT FALSE,
    added_to_cart BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
);

-- Insert sample product data for the 6 trained models
INSERT INTO products (garment_id, product_name, brand, category, description, price, discount_percent, image_path, model_available, stock_quantity) VALUES
('jin_17', 'Premium Jacket 17', 'JIN Fashion', 'Jacket', 'Stylish premium jacket with modern fit. Perfect for casual and semi-formal occasions. Made with high-quality materials for comfort and durability.', 89.99, 10, 'jin_17_white_bg.jpg', TRUE, 50),
('jin_18', 'Classic Jacket 18', 'JIN Fashion', 'Jacket', 'Classic design jacket that never goes out of style. Versatile and comfortable for everyday wear. Available in multiple sizes.', 79.99, 15, 'jin_18_white_bg.jpg', TRUE, 45),
('jin_22', 'Sport Jacket 22', 'JIN Fashion', 'Jacket', 'Athletic-inspired jacket with contemporary style. Perfect for active lifestyle and casual outings. Lightweight and breathable fabric.', 94.99, 5, 'jin_22_white_bg.jpg', TRUE, 40),
('lab_03', 'Professional Lab Coat 03', 'MediWear Pro', 'Lab Coat', 'Professional lab coat designed for medical professionals and laboratory work. Durable, comfortable, and easy to maintain. Multiple pockets for convenience.', 59.99, 0, 'lab_03_white_bg.jpg', TRUE, 60),
('lab_04', 'Comfort Lab Coat 04', 'MediWear Pro', 'Lab Coat', 'Comfort-focused lab coat with ergonomic design. Perfect for long hours of wear. Made with breathable fabric and reinforced stitching.', 64.99, 10, 'lab_04_white_bg.jpg', TRUE, 55),
('lab_07', 'Premium Lab Coat 07', 'MediWear Pro', 'Lab Coat', 'Premium quality lab coat with superior fabric and finish. Ideal for healthcare professionals who demand the best. Stain-resistant and easy-care.', 74.99, 0, 'lab_07_white_bg.jpg', TRUE, 50);

-- Insert size availability for all products
INSERT INTO product_sizes (product_id, size, stock_quantity, available)
SELECT product_id, 'S', 10, TRUE FROM products
UNION ALL
SELECT product_id, 'M', 15, TRUE FROM products
UNION ALL
SELECT product_id, 'L', 20, TRUE FROM products
UNION ALL
SELECT product_id, 'XL', 15, TRUE FROM products
UNION ALL
SELECT product_id, 'XXL', 10, TRUE FROM products;

-- Create views for easier querying
CREATE OR REPLACE VIEW product_catalog AS
SELECT 
    p.product_id,
    p.garment_id,
    p.product_name,
    p.brand,
    p.category,
    p.description,
    p.price,
    p.discount_percent,
    ROUND(p.price * (1 - p.discount_percent/100), 2) AS discounted_price,
    p.image_path,
    p.model_available,
    p.in_stock,
    p.stock_quantity
FROM products p
WHERE p.in_stock = TRUE;

CREATE OR REPLACE VIEW cart_details AS
SELECT 
    c.cart_id,
    c.user_id,
    u.username,
    p.product_id,
    p.product_name,
    p.brand,
    p.image_path,
    p.price,
    p.discount_percent,
    ROUND(p.price * (1 - p.discount_percent/100), 2) AS unit_price,
    c.size,
    c.quantity,
    ROUND(p.price * (1 - p.discount_percent/100) * c.quantity, 2) AS subtotal,
    c.added_at
FROM cart c
JOIN users u ON c.user_id = u.user_id
JOIN products p ON c.product_id = p.product_id;

COMMIT;
