CREATE TABLE customers (
    customer_id BIGSERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INTEGER,
    email VARCHAR(100),
    country VARCHAR(50),
    city VARCHAR(100),
    postal_code VARCHAR(50),
    phone_number VARCHAR(50),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_date TIMESTAMP
);

CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(customer_id) ON DELETE CASCADE,
    order_date TIMESTAMP,
    total_amount DECIMAL(10,2),
    status VARCHAR(50),
    shipping_address VARCHAR(100),
    payment_method VARCHAR(50),
    currency VARCHAR(3)
);

CREATE TABLE suppliers (
    supplier_id BIGSERIAL PRIMARY KEY,
    company_name VARCHAR(100),
    contact_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(50),
    country VARCHAR(50),
    lead_time INTEGER
);
COMMENT ON COLUMN suppliers.lead_time IS 'Measured in days';

CREATE TABLE products (
    product_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    cost DECIMAL(10,2),
    supplier_id BIGINT REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    stock_quantity INTEGER,
    weight DECIMAL,
    dimensions VARCHAR(50)
);

CREATE TABLE order_items (
    order_id BIGINT REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id BIGINT REFERENCES products(product_id) ON DELETE CASCADE,
    quantity INTEGER,
    unit_price DECIMAL(10,2),
    discount_amount DECIMAL(10,2),
    total_price DECIMAL(10,2),
    PRIMARY KEY(order_id, product_id)
);

CREATE TABLE product_reviews (
    review_id BIGSERIAL PRIMARY KEY,
    product_id BIGINT REFERENCES products(product_id) ON DELETE CASCADE,
    customer_id BIGINT REFERENCES customers(customer_id) ON DELETE CASCADE,
    rating INTEGER,
    review_text TEXT,
    review_date TIMESTAMP
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_suppliers_country ON suppliers(country);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_subcategory ON products(subcategory);
CREATE INDEX idx_reviews_product ON product_reviews(product_id);
