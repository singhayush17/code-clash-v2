from __future__ import annotations

import json
import sqlite3
import re
from dataclasses import dataclass
from typing import Any


MAX_ROWS = 200


SCHEMA = """
CREATE TABLE products (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  price REAL NOT NULL,
  stock INTEGER NOT NULL,
  rating REAL,
  discontinued INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  city TEXT NOT NULL,
  country TEXT NOT NULL,
  signup_date TEXT NOT NULL,
  tier TEXT NOT NULL,
  referrer_id INTEGER REFERENCES customers(id)
);

CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  ordered_at TEXT NOT NULL,
  status TEXT NOT NULL,
  channel TEXT NOT NULL
);

CREATE TABLE order_items (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(id),
  product_id INTEGER NOT NULL REFERENCES products(id),
  quantity INTEGER NOT NULL,
  unit_price REAL NOT NULL
);

CREATE TABLE shipments (
  id INTEGER PRIMARY KEY,
  order_id INTEGER NOT NULL REFERENCES orders(id),
  carrier TEXT NOT NULL,
  shipped_at TEXT,
  delivered_at TEXT,
  shipping_cost REAL NOT NULL
);

CREATE TABLE employees (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  team TEXT NOT NULL,
  manager_id INTEGER REFERENCES employees(id),
  hired_at TEXT NOT NULL,
  salary INTEGER NOT NULL
);

CREATE TABLE support_tickets (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER NOT NULL REFERENCES customers(id),
  order_id INTEGER REFERENCES orders(id),
  priority TEXT NOT NULL,
  status TEXT NOT NULL,
  opened_at TEXT NOT NULL,
  resolved_at TEXT
);
"""


SEED: dict[str, list[tuple[Any, ...]]] = {
    "products": [
        (1, "Mechanical Keyboard", "Electronics", 89.99, 34, 4.7, 0),
        (2, "USB-C Hub", "Electronics", 42.50, 58, 4.4, 0),
        (3, "Noise Cancelling Headphones", "Electronics", 149.00, 19, 4.8, 0),
        (4, "Standing Desk Mat", "Office", 36.00, 41, 4.2, 0),
        (5, "Notebook Pack", "Office", 12.75, 120, 4.1, 0),
        (6, "Desk Lamp", "Office", 36.00, 64, 4.3, 0),
        (7, "Travel Mug", "Kitchen", 18.25, 76, 4.0, 0),
        (8, "Pour Over Kit", "Kitchen", 31.80, 22, 4.6, 0),
        (9, "Alpine Rucksack", "Outdoor", 89.99, 15, 4.5, 0),
        (10, "Windbreaker", "Outdoor", 95.00, 0, 4.2, 0),
        (11, "Balance Block", "Fitness", 10.00, 15, 3.9, 0),
        (12, "Smart Scale", "Fitness", 55.00, 0, 4.0, 1),
    ],
    "customers": [
        (1, "Asha Rao", "Bengaluru", "India", "2023-01-12", "gold", None),
        (2, "Noah Kim", "Seoul", "South Korea", "2023-02-20", "silver", 1),
        (3, "Mia Chen", "Singapore", "Singapore", "2023-03-05", "gold", 1),
        (4, "Luis Garcia", "Austin", "USA", "2023-03-18", "bronze", None),
        (5, "Emma Stone", "London", "UK", "2023-04-22", "silver", 3),
        (6, "Kabir Mehta", "Mumbai", "India", "2023-03-05", "gold", 1),
        (7, "Zoe Miller", "Berlin", "Germany", "2023-07-17", "bronze", 5),
        (8, "Ivy Tan", "Singapore", "Singapore", "2023-09-30", "silver", 3),
    ],
    "orders": [
        (101, 1, "2024-01-05", "delivered", "web"),
        (102, 2, "2024-01-09", "delivered", "mobile"),
        (103, 3, "2024-01-11", "cancelled", "web"),
        (104, 1, "2024-01-09", "delivered", "web"),
        (105, 4, "2024-02-10", "processing", "mobile"),
        (106, 5, "2024-02-14", "delivered", "store"),
        (107, 6, "2024-03-03", "shipped", "web"),
        (108, 3, "2024-03-09", "delivered", "mobile"),
        (109, 8, "2024-03-03", "processing", "web"),
        (110, 7, "2024-04-01", "delivered", "web"),
    ],
    "order_items": [
        (1001, 101, 1, 1, 89.99),
        (1002, 101, 5, 3, 12.75),
        (1003, 102, 2, 1, 42.50),
        (1004, 102, 7, 2, 18.25),
        (1005, 103, 3, 1, 149.00),
        (1006, 104, 8, 1, 31.80),
        (1007, 104, 6, 2, 36.00),
        (1008, 105, 10, 1, 95.00),
        (1009, 106, 4, 2, 36.00),
        (1010, 106, 5, 5, 12.75),
        (1011, 107, 9, 1, 72.00),
        (1012, 107, 7, 1, 18.25),
        (1013, 108, 1, 1, 89.99),
        (1014, 108, 2, 2, 42.50),
        (1015, 109, 11, 4, 10.00),
        (1016, 110, 3, 1, 149.00),
        (1017, 110, 6, 1, 36.00),
    ],
    "shipments": [
        (1, 101, "ShipFast", "2024-01-06", "2024-01-09", 6.50),
        (2, 102, "BluePost", "2024-01-10", "2024-01-14", 5.75),
        (3, 104, "ShipFast", "2024-02-03", "2024-02-06", 7.25),
        (4, 106, "QuickKart", "2024-02-15", "2024-02-17", 4.95),
        (5, 107, "BluePost", "2024-03-04", None, 8.10),
        (6, 108, "ShipFast", "2024-03-10", "2024-03-12", 6.00),
        (7, 110, "QuickKart", "2024-04-02", "2024-04-05", 9.50),
    ],
    "employees": [
        (1, "Rina Kapoor", "Leadership", None, "2020-01-15", 140000),
        (2, "Owen Brooks", "Engineering", 1, "2021-03-12", 118000),
        (3, "Priya Nair", "Data", 1, "2021-07-01", 112000),
        (4, "Sam Wilson", "Support", 1, "2022-02-19", 76000),
        (5, "Mei Lin", "Engineering", 2, "2022-06-22", 98000),
        (6, "Arjun Sen", "Data", 3, "2022-09-05", 93000),
        (7, "Nora Evans", "Support", 4, "2023-01-18", 69000),
        (8, "Leo Park", "Operations", 1, "2023-05-11", 84000),
    ],
    "support_tickets": [
        (1, 1, 101, "high", "closed", "2024-01-08", "2024-01-09"),
        (2, 2, 102, "low", "closed", "2024-01-11", "2024-01-12"),
        (3, 3, 103, "medium", "closed", "2024-01-12", "2024-01-12"),
        (4, 4, 105, "high", "open", "2024-02-11", None),
        (5, 6, 107, "medium", "open", "2024-03-05", None),
        (6, 8, 109, "low", "pending", "2024-03-20", None),
        (7, 7, 110, "high", "closed", "2024-04-04", "2024-04-05"),
    ],
}


@dataclass(frozen=True)
class Task:
    id: str
    prompt: str
    starter: str
    solution: str
    verifier: str | None = None
    hint: str = ""


@dataclass(frozen=True)
class Lesson:
    id: str
    number: int
    title: str
    focus: list[str]
    tables: list[str]
    tasks: list[Task]


LESSONS = [
    Lesson("select-columns", 1, "SELECT Columns", ["SELECT", "FROM", "*", "LOWER", "UPPER"], ["products", "customers"], [
        Task("l1-t1", "Show every product name.", "", "SELECT name FROM products ORDER BY id;", hint="Return only the name column."),
        Task("l1-t2", "Show product names with their categories.", "", "SELECT name, category FROM products ORDER BY id;", hint="List two columns after SELECT."),
        Task("l1-t3", "Show the full products table.", "", "SELECT * FROM products ORDER BY id;", hint="Use the star shorthand."),
        Task("l1-t4", "Show product id, name, price, and stock from the products table.", "", "SELECT id, name, price, stock FROM products ORDER BY id;"),
        Task("l1-t5", "Show customer names and cities from the customers table.", "", "SELECT name, city FROM customers ORDER BY id;"),
        Task("l1-t6", "Show all product names in lowercase (as 'name_lower'), sorted by name_lower.", "", "SELECT LOWER(name) AS name_lower FROM products ORDER BY name_lower;"),
        Task("l1-t7", "Show all customer names in uppercase (as 'name_upper') with their country, sorted by name_upper.", "", "SELECT UPPER(name) AS name_upper, country FROM customers ORDER BY name_upper;"),
        Task("l1-t8", "Show product names where the lowercase name contains 'kit'. Show name, sorted by name.", "", "SELECT name FROM products WHERE LOWER(name) LIKE '%kit%' ORDER BY name;"),
    ]),
    Lesson("where-numeric", 2, "WHERE Constraints", ["WHERE", "AND", "OR"], ["products", "orders"], [
        Task("l2-t1", "Find products priced at 50 or more. Show name and price, sorted by price then name.", "", "SELECT name, price FROM products WHERE price >= 50 ORDER BY price, name;"),
        Task("l2-t2", "Find products with stock below 20. Show name and stock, sorted by stock then name.", "", "SELECT name, stock FROM products WHERE stock < 20 ORDER BY stock, name;"),
        Task("l2-t3", "Find electronics with a rating of at least 4.5. Show name, category, and rating, sorted by rating descending.", "", "SELECT name, category, rating FROM products WHERE category = 'Electronics' AND rating >= 4.5 ORDER BY rating DESC;"),
        Task("l2-t4", "Find orders that are processing or shipped. Show id and status, sorted by id.", "", "SELECT id, status FROM orders WHERE status = 'processing' OR status = 'shipped' ORDER BY id;"),
        Task("l2-t5", "Find active (not discontinued) products with zero stock. Show name, stock, and discontinued, sorted by id.", "", "SELECT name, stock, discontinued FROM products WHERE stock = 0 AND discontinued = 0 ORDER BY id;"),
    ]),
    Lesson("where-text", 3, "Text and NULL Filters", ["LIKE", "IN", "IS NULL"], ["customers", "shipments", "support_tickets"], [
        Task("l3-t1", "Find customers from India or Singapore. Show name and country, sorted by name.", "", "SELECT name, country FROM customers WHERE country IN ('India', 'Singapore') ORDER BY name;"),
        Task("l3-t2", "Find customers whose name contains the letter 'a' (case-insensitive). Show name, sorted by name.", "", "SELECT name FROM customers WHERE lower(name) LIKE '%a%' ORDER BY name;"),
        Task("l3-t3", "Find shipments that have not been delivered yet. Show order_id, carrier, and delivered_at, sorted by order_id.", "", "SELECT order_id, carrier, delivered_at FROM shipments WHERE delivered_at IS NULL ORDER BY order_id;"),
        Task("l3-t4", "Find open or pending support tickets. Show id, customer_id, and status, sorted by id.", "", "SELECT id, customer_id, status FROM support_tickets WHERE status IN ('open', 'pending') ORDER BY id;"),
        Task("l3-t5", "Find customers without a referrer. Show name and referrer_id, sorted by name.", "", "SELECT name, referrer_id FROM customers WHERE referrer_id IS NULL ORDER BY name;"),
    ]),
    Lesson("sorting-limits", 4, "Sorting and Limits", ["ORDER BY", "LIMIT", "DISTINCT"], ["products", "customers", "orders"], [
        Task("l4-t1", "Show the five most expensive products. Return name and price, ordered by price descending then name.", "", "SELECT name, price FROM products ORDER BY price DESC, name LIMIT 5;"),
        Task("l4-t2", "List all product categories once, alphabetically.", "", "SELECT DISTINCT category FROM products ORDER BY category;"),
        Task("l4-t3", "Show the three newest customers. Return name and signup_date.", "", "SELECT name, signup_date FROM customers ORDER BY signup_date DESC LIMIT 3;"),
        Task("l4-t4", "Show delivered orders ordered from newest to oldest. Return id, ordered_at, and status.", "", "SELECT id, ordered_at, status FROM orders WHERE status = 'delivered' ORDER BY ordered_at DESC, id DESC;"),
        Task("l4-t5", "Show products sorted by category, then by highest price within each category, then by name. Return name, category, and price.", "", "SELECT name, category, price FROM products ORDER BY category, price DESC, name;"),
    ]),
    Lesson("select-review", 5, "SELECT Review", ["SELECT", "WHERE", "ORDER BY"], ["products", "customers", "orders"], [
        Task("l5-t1", "Find non-discontinued products with price less than 30. Show name and price, sorted by price.", "", "SELECT name, price FROM products WHERE discontinued = 0 AND price < 30 ORDER BY price;"),
        Task("l5-t2", "Show gold-tier customers outside India. Return name, country, and tier, sorted by name.", "", "SELECT name, country, tier FROM customers WHERE tier = 'gold' AND country <> 'India' ORDER BY name;"),
        Task("l5-t3", "Show web orders placed in March 2024. Return id, customer_id, and ordered_at, sorted by ordered_at.", "", "SELECT id, customer_id, ordered_at FROM orders WHERE channel = 'web' AND ordered_at >= '2024-03-01' AND ordered_at < '2024-04-01' ORDER BY ordered_at;"),
        Task("l5-t4", "Show the two lowest-stock active (not discontinued) products. Return name and stock, sorted by stock.", "", "SELECT name, stock FROM products WHERE discontinued = 0 ORDER BY stock LIMIT 2;"),
        Task("l5-t5", "Show name, city, and tier for silver-tier customers, sorted by city.", "", "SELECT name, city, tier FROM customers WHERE tier = 'silver' ORDER BY city;"),
    ]),
    Lesson("inner-joins", 6, "INNER JOINs", ["JOIN", "ON"], ["orders", "customers", "order_items", "products"], [
        Task("l6-t1", "Show each order id with the customer name, sorted by order id.", "", "SELECT orders.id, customers.name FROM orders JOIN customers ON customers.id = orders.customer_id ORDER BY orders.id;"),
        Task("l6-t2", "Show each order item's order_id, product name, and quantity, sorted by order_id then product name.", "", "SELECT order_items.order_id, products.name, order_items.quantity FROM order_items JOIN products ON products.id = order_items.product_id ORDER BY order_items.order_id, products.name;"),
        Task("l6-t3", "Show delivered orders with their id, customer name, and channel, sorted by order id.", "", "SELECT orders.id, customers.name, orders.channel FROM orders JOIN customers ON customers.id = orders.customer_id WHERE orders.status = 'delivered' ORDER BY orders.id;"),
        Task("l6-t4", "Show the product name and category for items in order 108, sorted by product name.", "", "SELECT products.name, products.category FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id = 108 ORDER BY products.name;"),
        Task("l6-t5", "Show customer name (as 'customer'), product name (as 'product'), and quantity for every order item, sorted by order id then product name.", "", "SELECT customers.name AS customer, products.name AS product, order_items.quantity FROM orders JOIN customers ON customers.id = orders.customer_id JOIN order_items ON order_items.order_id = orders.id JOIN products ON products.id = order_items.product_id ORDER BY orders.id, products.name;"),
        Task("l6-t6", "Find the names of customers who purchased 'Mechanical Keyboard'. Show customer name and city, sorted by city.", "", "SELECT c.name, c.city FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE p.name = 'Mechanical Keyboard' ORDER BY c.city;"),
        Task("l6-t7", "Show product names and their corresponding order statuses for all items in order 101, sorted by product name.", "", "SELECT p.name, o.status FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON o.id = oi.order_id WHERE o.id = 101 ORDER BY p.name;"),
        Task("l6-t8", "Find all customers from 'Singapore' who have placed an order. Show customer name and order id, sorted by order id.", "", "SELECT c.name, o.id FROM customers c JOIN orders o ON o.customer_id = c.id WHERE c.country = 'Singapore' ORDER BY o.id;"),
        Task("l6-t9", "List all products and their unit prices for orders that were placed via the 'mobile' channel. Show product name, unit_price, and channel, sorted by product name.", "", "SELECT p.name, oi.unit_price, o.channel FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON o.id = oi.order_id WHERE o.channel = 'mobile' ORDER BY p.name;"),
        Task("l6-t10", "Show customer name, product name, and quantity for all 'delivered' orders. Sort by customer name then product name.", "", "SELECT c.name, p.name, oi.quantity FROM customers c JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id JOIN products p ON p.id = oi.product_id WHERE o.status = 'delivered' ORDER BY c.name, p.name;"),
        Task("l6-t11", "Find the names of products and the carrier name for every order that has a recorded shipment. Sort by carrier then product name.", "", "SELECT p.name, s.carrier FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON o.id = oi.order_id JOIN shipments s ON s.order_id = o.id ORDER BY s.carrier, p.name;"),
        Task("l6-t12", "List all customers who have a support ticket with 'high' priority. Show customer name, ticket status, and order id, sorted by customer name.", "", "SELECT c.name, st.status, st.order_id FROM customers c JOIN support_tickets st ON st.customer_id = c.id WHERE st.priority = 'high' ORDER BY c.name;"),
        Task("l6-t13", "Show product names and categories for orders placed by customers in the 'gold' tier. Sort by category then product name.", "", "SELECT p.name, p.category FROM products p JOIN order_items oi ON oi.product_id = p.id JOIN orders o ON o.id = oi.order_id JOIN customers c ON c.id = o.customer_id WHERE c.tier = 'gold' ORDER BY p.category, p.name;"),
        Task("l6-t14", "Find products that have more than 2 units in a single order line. Show product name, quantity, and order id, sorted by quantity desc.", "", "SELECT p.name, oi.quantity, oi.order_id FROM products p JOIN order_items oi ON oi.product_id = p.id WHERE oi.quantity > 2 ORDER BY oi.quantity DESC;"),
        Task("l6-t15", "Show the names of employees and their hired_at date for those who report to 'Rina Kapoor'. Sort by name.", "", "SELECT e.name, e.hired_at FROM employees e JOIN employees m ON e.manager_id = m.id WHERE m.name = 'Rina Kapoor' ORDER BY e.name;"),
    ]),
    Lesson("outer-joins", 7, "LEFT JOINs", ["LEFT JOIN", "missing rows"], ["products", "order_items", "orders", "shipments"], [
        Task("l7-t1", "Show every product name and any order item id (as 'item_id') that references it, sorted by product name. Use a LEFT JOIN.", "", "SELECT products.name, order_items.id AS item_id FROM products LEFT JOIN order_items ON order_items.product_id = products.id ORDER BY products.name;"),
        Task("l7-t2", "Find products that have never been ordered. Show name, sorted by name. Use a LEFT JOIN.", "", "SELECT products.name FROM products LEFT JOIN order_items ON order_items.product_id = products.id WHERE order_items.id IS NULL ORDER BY products.name;"),
        Task("l7-t3", "Show every order's id, status, and delivered_at from shipments (NULL if no shipment), sorted by order id. Use a LEFT JOIN.", "", "SELECT orders.id, orders.status, shipments.delivered_at FROM orders LEFT JOIN shipments ON shipments.order_id = orders.id ORDER BY orders.id;"),
        Task("l7-t4", "Find orders with no shipment row. Show id and status, sorted by id. Use a LEFT JOIN.", "", "SELECT orders.id, orders.status FROM orders LEFT JOIN shipments ON shipments.order_id = orders.id WHERE shipments.id IS NULL ORDER BY orders.id;"),
        Task("l7-t5", "Show all customer names and the id of any order they placed (as 'order_id'), sorted by customer name. Use a LEFT JOIN.", "", "SELECT customers.name, orders.id AS order_id FROM customers LEFT JOIN orders ON orders.customer_id = customers.id ORDER BY customers.name;"),
    ]),
    Lesson("self-joins", 8, "Self Joins", ["self join", "hierarchies"], ["employees", "customers"], [
            Task("l30-t1", "Show each employee name (as 'employee') with their manager name (as 'manager'). Use a LEFT JOIN on employees. Sort by employee name.", "", "SELECT e.name AS employee, m.name AS manager FROM employees e LEFT JOIN employees m ON m.id = e.manager_id ORDER BY e.name;"),
            Task("l30-t2", "Show each customer name (as 'customer') with their referrer name (as 'referrer'). Use a LEFT JOIN on customers. Sort by customer name.", "", "SELECT c.name AS customer, r.name AS referrer FROM customers c LEFT JOIN customers r ON r.id = c.referrer_id ORDER BY c.name;"),
            Task("l30-t3", "Find pairs of customers from the same country without duplicate mirrored pairs (a.id < b.id). Show customer_a, customer_b, and country. Sort by country.", "", "SELECT a.name AS customer_a, b.name AS customer_b, a.country FROM customers a JOIN customers b ON a.country = b.country AND a.id < b.id ORDER BY a.country;"),
            Task("l30-t4", "Find employees who share a manager (exclude NULL managers, use a.id < b.id). Show employee_a, employee_b, and manager_id. Sort by employee_a.", "", "SELECT a.name AS employee_a, b.name AS employee_b, a.manager_id FROM employees a JOIN employees b ON a.manager_id = b.manager_id AND a.id < b.id WHERE a.manager_id IS NOT NULL ORDER BY employee_a;"),
            Task("l30-t5", "Show manager names (as 'manager') and how many direct reports they have (as 'direct_reports'). Join employees to itself. Sort by direct_reports descending.", "", "SELECT managers.name AS manager, COUNT(reports.id) AS direct_reports FROM employees managers JOIN employees reports ON reports.manager_id = managers.id GROUP BY managers.id, managers.name ORDER BY direct_reports DESC;"),
        ]),
    Lesson("semi-anti-joins", 9, "EXISTS and Anti-Joins", ["EXISTS", "NOT EXISTS"], ["customers", "orders", "products", "order_items", "shipments"], [
            Task("l29-t1", "Find customers who have at least one delivered order using EXISTS. Show name, sorted by name.", "", "SELECT name FROM customers WHERE EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id AND orders.status = 'delivered') ORDER BY name;"),
            Task("l29-t2", "Find customers who have never placed an order using NOT EXISTS. Show name, sorted by name.", "", "SELECT name FROM customers WHERE NOT EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id) ORDER BY name;"),
            Task("l29-t3", "Find products that have never been ordered using NOT EXISTS. Show name, sorted by name.", "", "SELECT name FROM products WHERE NOT EXISTS (SELECT 1 FROM order_items WHERE order_items.product_id = products.id) ORDER BY name;"),
            Task("l29-t4", "Find orders that have a shipment row using EXISTS. Show id, sorted by id.", "", "SELECT id FROM orders WHERE EXISTS (SELECT 1 FROM shipments WHERE shipments.order_id = orders.id) ORDER BY id;"),
            Task("l29-t5", "Find delivered orders that do not have a support ticket using NOT EXISTS. Show id, sorted by id.", "", "SELECT id FROM orders WHERE status = 'delivered' AND NOT EXISTS (SELECT 1 FROM support_tickets WHERE support_tickets.order_id = orders.id) ORDER BY id;"),
        ]),
    Lesson("nulls", 10, "Working with NULL", ["IS NULL", "COALESCE"], ["customers", "employees", "shipments"], [
        Task("l8-t1", "Show customer name and referrer id as 'referrer', replacing NULL referrer_id with 'Direct' using COALESCE. Sort by name.", "", "SELECT name, COALESCE(CAST(referrer_id AS TEXT), 'Direct') AS referrer FROM customers ORDER BY name;"),
        Task("l8-t2", "Find employees who do not have a manager. Show name and team, sorted by name.", "", "SELECT name, team FROM employees WHERE manager_id IS NULL ORDER BY name;"),
        Task("l8-t3", "Show each shipment's order_id and a 'delivery_status' label: 'Delivered' if delivered_at exists, otherwise 'In transit'. Sort by order_id.", "", "SELECT order_id, CASE WHEN delivered_at IS NULL THEN 'In transit' ELSE 'Delivered' END AS delivery_status FROM shipments ORDER BY order_id;"),
        Task("l8-t4", "Show support tickets with no resolved date. Return id, status, and resolved_at, sorted by id.", "", "SELECT id, status, resolved_at FROM support_tickets WHERE resolved_at IS NULL ORDER BY id;"),
        Task("l8-t5", "Show each employee's name and their manager's name as 'manager', using 'No manager' when there is no manager. Sort by employee id.", "", "SELECT e.name, COALESCE(m.name, 'No manager') AS manager FROM employees e LEFT JOIN employees m ON m.id = e.manager_id ORDER BY e.id;"),
    ]),
    Lesson("expressions", 11, "Expressions", ["AS", "CASE", "calculation"], ["order_items", "products", "employees"], [
        Task("l9-t1", "Show each order item's order_id, product_id, and subtotal (quantity × unit_price, as 'subtotal'), sorted by order_id then product_id.", "", "SELECT order_id, product_id, quantity * unit_price AS subtotal FROM order_items ORDER BY order_id, product_id;"),
        Task("l9-t2", "Show each product's name and price increased by 10% as 'projected_price', rounded to 2 decimals. Sort by name.", "", "SELECT name, ROUND(price * 1.10, 2) AS projected_price FROM products ORDER BY name;"),
        Task("l9-t3", "Show product name and a 'stock_status' label: 'Low stock' when stock < 20, otherwise 'Ready'. Sort by name.", "", "SELECT name, CASE WHEN stock < 20 THEN 'Low stock' ELSE 'Ready' END AS stock_status FROM products ORDER BY name;"),
        Task("l9-t4", "Show each employee's name and monthly salary (salary / 12, rounded to 2 decimals, as 'monthly_salary'). Sort by name.", "", "SELECT name, ROUND(salary / 12.0, 2) AS monthly_salary FROM employees ORDER BY name;"),
        Task("l9-t5", "Show each order item's order_id and discounted subtotal (quantity × unit_price × 0.95, rounded to 2 decimals, as 'discounted_subtotal'). Sort by order_id then discounted_subtotal.", "", "SELECT order_id, ROUND(quantity * unit_price * 0.95, 2) AS discounted_subtotal FROM order_items ORDER BY order_id, discounted_subtotal;"),
    ]),
    Lesson("string-functions", 12, "String Functions", ["LOWER", "SUBSTR", "LENGTH"], ["customers", "products"], [
            Task("l21-t1", "Show customer names in lowercase (as 'name_lower') with their city, sorted by name_lower.", "", "SELECT lower(name) AS name_lower, city FROM customers ORDER BY name_lower;"),
            Task("l21-t2", "Show product name and the first four characters of each category (as 'category_prefix'), sorted by name.", "", "SELECT name, substr(category, 1, 4) AS category_prefix FROM products ORDER BY name;"),
            Task("l21-t3", "Find customers whose city name has more than 6 characters. Show name, city, and length(city) as 'city_length', sorted by city_length descending.", "", "SELECT name, city, length(city) AS city_length FROM customers WHERE length(city) > 6 ORDER BY city_length DESC;"),
            Task("l21-t4", "Build a customer label formatted as 'name - country' (as 'customer_label'), sorted by customer_label.", "", "SELECT name || ' - ' || country AS customer_label FROM customers ORDER BY customer_label;"),
            Task("l21-t5", "Find products whose lowercase name contains 'usb' or 'desk'. Show name, sorted by name.", "", "SELECT name FROM products WHERE lower(name) LIKE '%usb%' OR lower(name) LIKE '%desk%' ORDER BY name;"),
        ]),
    Lesson("date-analytics", 13, "Date Analytics", ["strftime", "julianday", "cohorts"], ["customers", "orders", "shipments"], [
            Task("l22-t1", "Count orders by calendar month. Show month (first 7 chars of ordered_at, as 'order_month') and count as 'order_count', sorted by order_month.", "", "SELECT substr(ordered_at, 1, 7) AS order_month, COUNT(*) AS order_count FROM orders GROUP BY order_month ORDER BY order_month;"),
            Task("l22-t2", "Find the number of days between shipment and delivery for delivered shipments. Show order_id and days as 'delivery_days' (integer), sorted by order_id.", "", "SELECT order_id, CAST(julianday(delivered_at) - julianday(shipped_at) AS INTEGER) AS delivery_days FROM shipments WHERE delivered_at IS NOT NULL ORDER BY order_id;"),
            Task("l22-t3", "Show customer name and signup quarter (as 'signup_quarter', formatted like 'Q1'). Sort by signup_date.", "", "SELECT name, 'Q' || ((CAST(strftime('%m', signup_date) AS INTEGER) + 2) / 3) AS signup_quarter FROM customers ORDER BY signup_date;"),
            Task("l22-t4", "Find orders placed in Q1 2024 (Jan-Mar). Show id and ordered_at, sorted by ordered_at.", "", "SELECT id, ordered_at FROM orders WHERE ordered_at >= '2024-01-01' AND ordered_at < '2024-04-01' ORDER BY ordered_at;"),
            Task("l22-t5", "Calculate days from each customer's signup to their first order (as 'days_to_first_order', integer). Join customers and orders, group by customer. Sort by days_to_first_order.", "", "SELECT customers.name, CAST(julianday(MIN(orders.ordered_at)) - julianday(customers.signup_date) AS INTEGER) AS days_to_first_order FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name, customers.signup_date ORDER BY days_to_first_order;"),
        ]),
    Lesson("data-cleaning", 14, "Data Cleaning Queries", ["TRIM", "COALESCE", "CASE"], ["customers", "products", "shipments"], [
            Task("l33-t1", "Show customer name and tier in uppercase (as 'tier_label'). Sort by name.", "", "SELECT name, upper(tier) AS tier_label FROM customers ORDER BY name;"),
            Task("l33-t2", "Show product name and rating, replacing NULL ratings with 0 (as 'rating_safe'). Sort by name.", "", "SELECT name, COALESCE(rating, 0) AS rating_safe FROM products ORDER BY name;"),
            Task("l33-t3", "Classify products by price: 'budget' if price < 25, 'standard' if price < 75, else 'premium' (as 'price_band'). Show name and price_band, sorted by price then name.", "", "SELECT name, CASE WHEN price < 25 THEN 'budget' WHEN price < 75 THEN 'standard' ELSE 'premium' END AS price_band FROM products ORDER BY price, name;"),
            Task("l33-t4", "Show shipment order_id and delivery date, replacing NULL delivered_at with 'Pending' (as 'delivery_status'). Sort by order_id.", "", "SELECT order_id, COALESCE(delivered_at, 'Pending') AS delivery_status FROM shipments ORDER BY order_id;"),
            Task("l33-t5", "Create a normalized product key by lowercasing the name and replacing spaces with hyphens (as 'product_key'). Show name and product_key, sorted by name.", "", "SELECT name, replace(lower(name), ' ', '-') AS product_key FROM products ORDER BY name;"),
        ]),
    Lesson("aggregates", 15, "Aggregates", ["COUNT", "SUM", "AVG"], ["products", "orders", "order_items"], [
        Task("l10-t1", "Count all products. Alias the result as 'product_count'.", "", "SELECT COUNT(*) AS product_count FROM products;"),
        Task("l10-t2", "Find the average product price, rounded to 2 decimals. Alias as 'average_price'.", "", "SELECT ROUND(AVG(price), 2) AS average_price FROM products;"),
        Task("l10-t3", "Find the total revenue from all order items (sum of quantity × unit_price), rounded to 2 decimals. Alias as 'revenue'.", "", "SELECT ROUND(SUM(quantity * unit_price), 2) AS revenue FROM order_items;"),
        Task("l10-t4", "Find the lowest and highest product price. Alias as 'lowest_price' and 'highest_price'.", "", "SELECT MIN(price) AS lowest_price, MAX(price) AS highest_price FROM products;"),
        Task("l10-t5", "Count orders grouped by status. Show status and count as 'order_count', sorted by status.", "", "SELECT status, COUNT(*) AS order_count FROM orders GROUP BY status ORDER BY status;"),
    ]),
    Lesson("grouping", 16, "GROUP BY and HAVING", ["GROUP BY", "HAVING"], ["products", "orders", "order_items", "customers"], [
        Task("l11-t1", "Count products in each category. Show category and count as 'product_count', sorted by category.", "", "SELECT category, COUNT(*) AS product_count FROM products GROUP BY category ORDER BY category;"),
        Task("l11-t2", "Find total revenue per order (sum of quantity × unit_price, rounded to 2 decimals). Show order_id and total as 'order_total', sorted by order_id.", "", "SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS order_total FROM order_items GROUP BY order_id ORDER BY order_id;"),
        Task("l11-t3", "Find customers with more than one order. Join customers with orders. Show customer name and count as 'order_count', sorted by name.", "", "SELECT customers.name, COUNT(orders.id) AS order_count FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name HAVING COUNT(orders.id) > 1 ORDER BY customers.name;"),
        Task("l11-t4", "Find product categories whose average price exceeds 50. Show category and average as 'average_price' (rounded to 2 decimals), sorted by category.", "", "SELECT category, ROUND(AVG(price), 2) AS average_price FROM products GROUP BY category HAVING AVG(price) > 50 ORDER BY category;"),
        Task("l11-t5", "Find total quantity sold for each product. Join products with order_items. Show product name and sum as 'units_sold', sorted by units_sold descending then name.", "", "SELECT products.name, SUM(order_items.quantity) AS units_sold FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name ORDER BY units_sold DESC, products.name;"),
    ]),
    Lesson("conditional-aggregation", 17, "Conditional Aggregation", ["SUM(CASE)", "COUNT(CASE)"], ["orders", "order_items", "customers", "products"], [
            Task("l23-t1", "For each order channel, count delivered orders (as 'delivered_orders') and non-delivered orders (as 'other_orders') using SUM(CASE...). Sort by channel.", "", "SELECT channel, SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders, SUM(CASE WHEN status <> 'delivered' THEN 1 ELSE 0 END) AS other_orders FROM orders GROUP BY channel ORDER BY channel;"),
            Task("l23-t2", "For each customer tier, count customers from India (as 'india_customers') and outside India (as 'other_customers') using SUM(CASE...). Sort by tier.", "", "SELECT tier, SUM(CASE WHEN country = 'India' THEN 1 ELSE 0 END) AS india_customers, SUM(CASE WHEN country <> 'India' THEN 1 ELSE 0 END) AS other_customers FROM customers GROUP BY tier ORDER BY tier;"),
            Task("l23-t3", "For each product category, count products with stock below 20 (as 'low_stock') and stock 20 or above (as 'healthy_stock') using SUM(CASE...). Sort by category.", "", "SELECT category, SUM(CASE WHEN stock < 20 THEN 1 ELSE 0 END) AS low_stock, SUM(CASE WHEN stock >= 20 THEN 1 ELSE 0 END) AS healthy_stock FROM products GROUP BY category ORDER BY category;"),
            Task("l23-t4", "For each customer, calculate delivered revenue (as 'delivered_revenue') and cancelled revenue (as 'cancelled_revenue') separately, rounded to 2 decimals. Join customers, orders, and order_items. Sort by customer name.", "", "SELECT customers.name, ROUND(SUM(CASE WHEN orders.status = 'delivered' THEN order_items.quantity * order_items.unit_price ELSE 0 END), 2) AS delivered_revenue, ROUND(SUM(CASE WHEN orders.status = 'cancelled' THEN order_items.quantity * order_items.unit_price ELSE 0 END), 2) AS cancelled_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name ORDER BY customers.name;"),
            Task("l23-t5", "Show total units sold split into Electronics units (as 'electronics_units') and all other units (as 'non_electronics_units') using SUM(CASE...). Join products and order_items.", "", "SELECT SUM(CASE WHEN products.category = 'Electronics' THEN order_items.quantity ELSE 0 END) AS electronics_units, SUM(CASE WHEN products.category <> 'Electronics' THEN order_items.quantity ELSE 0 END) AS non_electronics_units FROM products JOIN order_items ON order_items.product_id = products.id;"),
        ]),
    Lesson("union-intersect-except", 18, "UNION / INTERSECT / EXCEPT", ["UNION", "UNION ALL", "INTERSECT", "EXCEPT"], ["customers", "orders", "products", "order_items", "shipments"], [
        Task("l19u-t1", "List every distinct country that appears in the customers table combined with the single value 'Canada'. Show country, sorted alphabetically. Use UNION.", "", "SELECT country FROM customers UNION SELECT 'Canada' AS country ORDER BY country;"),
        Task("l19u-t2", "Show all customer cities AND all shipment carriers in a single column named 'label'. Include duplicates. Sort by label. Use UNION ALL.", "", "SELECT city AS label FROM customers UNION ALL SELECT carrier AS label FROM shipments ORDER BY label;"),
        Task("l19u-t3", "Find countries that have BOTH gold-tier AND silver-tier customers. Show country, sorted by country. Use INTERSECT.", "", "SELECT country FROM customers WHERE tier = 'gold' INTERSECT SELECT country FROM customers WHERE tier = 'silver' ORDER BY country;"),
        Task("l19u-t4", "Find product ids that exist in the products table but have never appeared in order_items. Show id, sorted by id. Use EXCEPT.", "", "SELECT id FROM products EXCEPT SELECT product_id FROM order_items ORDER BY id;"),
        Task("l19u-t5", "Find customer ids who placed orders via 'web' AND via 'mobile' (both channels). Show customer_id, sorted. Use INTERSECT.", "", "SELECT customer_id FROM orders WHERE channel = 'web' INTERSECT SELECT customer_id FROM orders WHERE channel = 'mobile' ORDER BY customer_id;"),
        Task("l19u-t6", "Build a unified order status report: for each status show 'delivered', 'cancelled', or 'other' orders count. Use UNION ALL to combine three separate SELECT statements (one per status group), each returning status_group and order_count. Sort by status_group.", "", "SELECT 'delivered' AS status_group, COUNT(*) AS order_count FROM orders WHERE status = 'delivered' UNION ALL SELECT 'cancelled' AS status_group, COUNT(*) AS order_count FROM orders WHERE status = 'cancelled' UNION ALL SELECT 'other' AS status_group, COUNT(*) AS order_count FROM orders WHERE status NOT IN ('delivered', 'cancelled') ORDER BY status_group;"),
    ]),
    Lesson("set-operations-advanced", 19, "Set Operations", ["UNION", "INTERSECT", "EXCEPT"], ["customers", "orders", "products", "order_items"], [
            Task("l31-t1", "List countries that have both gold and silver customers using INTERSECT. Show country, sorted by country.", "", "SELECT country FROM customers WHERE tier = 'gold' INTERSECT SELECT country FROM customers WHERE tier = 'silver' ORDER BY country;"),
            Task("l31-t2", "List product ids that exist in products but not in order_items using EXCEPT. Show id, sorted by id.", "", "SELECT id FROM products EXCEPT SELECT product_id FROM order_items ORDER BY id;"),
            Task("l31-t3", "Combine customer cities and shipment carriers into a single column 'label' using UNION. Sort by label.", "", "SELECT city AS label FROM customers UNION SELECT carrier AS label FROM shipments ORDER BY label;"),
            Task("l31-t4", "Find customer_ids who ordered via both web and mobile using INTERSECT. Show customer_id, sorted by customer_id.", "", "SELECT customer_id FROM orders WHERE channel = 'web' INTERSECT SELECT customer_id FROM orders WHERE channel = 'mobile' ORDER BY customer_id;"),
            Task("l31-t5", "Find ordered product_ids that are not active stocked products (discontinued = 0 and stock > 0) using EXCEPT. Show product_id, sorted by product_id.", "", "SELECT product_id FROM order_items EXCEPT SELECT id FROM products WHERE discontinued = 0 AND stock > 0 ORDER BY product_id;"),
        ]),
    Lesson("advanced-review", 20, "Subqueries and Sets", ["subquery", "UNION", "EXCEPT"], ["products", "customers", "orders", "order_items"], [
        Task("l19-t1", "Find products priced above the overall average price. Show name and price, sorted by price descending then name.", "", "SELECT name, price FROM products WHERE price > (SELECT AVG(price) FROM products) ORDER BY price DESC, name;"),
        Task("l19-t2", "Find customers who have placed at least one delivered order. Show name, sorted by name. Use a subquery with IN.", "", "SELECT name FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE status = 'delivered') ORDER BY name;"),
        Task("l19-t3", "List all unique countries from customers combined with the literal value 'Canada' using UNION. Sort by country.", "", "SELECT country FROM customers UNION SELECT 'Canada' AS country ORDER BY country;"),
        Task("l19-t4", "Find products that have never appeared in order_items using EXCEPT. Show id and name, sorted by id.", "", "SELECT id, name FROM products EXCEPT SELECT products.id, products.name FROM products JOIN order_items ON order_items.product_id = products.id ORDER BY id;"),
        Task("l19-t5", "Find customers whose total non-cancelled spend exceeds the average order total. Show name and spend (rounded to 2 decimals, as 'spend'), sorted by spend descending.", "", "SELECT customer_totals.name, ROUND(customer_totals.spend, 2) AS spend FROM (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name) AS customer_totals WHERE customer_totals.spend > (SELECT AVG(order_total) FROM (SELECT SUM(quantity * unit_price) AS order_total FROM order_items GROUP BY order_id)) ORDER BY spend DESC;"),
    ]),
    Lesson("ctes", 21, "Common Table Expressions", ["WITH", "readability"], ["customers", "orders", "order_items", "products"], [
            Task("l27-t1", "Use a CTE named 'order_totals' to calculate each order's total, then return totals above 100. Show order_id and total (rounded to 2 decimals), sorted by total descending.", "", "WITH order_totals AS (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) SELECT order_id, ROUND(total, 2) AS total FROM order_totals WHERE total > 100 ORDER BY total DESC;"),
            Task("l27-t2", "Use two CTEs: 'customer_spend' (non-cancelled spend per customer) and 'avg_spend' (average of customer_spend). Return customers whose spend exceeds avg_spend. Show name and spend (rounded to 2 decimals), sorted by spend descending.", "", "WITH customer_spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name), avg_spend AS (SELECT AVG(spend) AS avg_spend FROM customer_spend) SELECT name, ROUND(spend, 2) AS spend FROM customer_spend, avg_spend WHERE spend > avg_spend ORDER BY spend DESC;"),
            Task("l27-t3", "Use a CTE named 'product_revenue' to find each product's revenue by category. Then sum by category. Show category and total as 'category_revenue' (rounded to 2 decimals), sorted by category_revenue descending.", "", "WITH product_revenue AS (SELECT products.category, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.category, products.name) SELECT category, ROUND(SUM(revenue), 2) AS category_revenue FROM product_revenue GROUP BY category ORDER BY category_revenue DESC;"),
            Task("l27-t4", "Use a CTE named 'delivered_orders' to filter delivered orders, then list distinct customer names, sorted by name.", "", "WITH delivered_orders AS (SELECT * FROM orders WHERE status = 'delivered') SELECT DISTINCT customers.name FROM delivered_orders JOIN customers ON customers.id = delivered_orders.customer_id ORDER BY customers.name;"),
            Task("l27-t5", "Use a CTE named 'category_counts' to count products per category, then keep categories with at least 2 products. Show category and product_count, sorted by category.", "", "WITH category_counts AS (SELECT category, COUNT(*) AS product_count FROM products GROUP BY category) SELECT category, product_count FROM category_counts WHERE product_count >= 2 ORDER BY category;"),
        ]),
    Lesson("recursive-ctes", 22, "Recursive CTEs", ["WITH RECURSIVE", "hierarchies"], ["employees", "customers"], [
            Task("l28-t1", "List the employee hierarchy starting from the top-level employee (no manager), including depth (0 for top). Show name and depth, sorted by depth then name.", "", "WITH RECURSIVE org(id, name, manager_id, depth) AS (SELECT id, name, manager_id, 0 FROM employees WHERE manager_id IS NULL UNION ALL SELECT employees.id, employees.name, employees.manager_id, org.depth + 1 FROM employees JOIN org ON employees.manager_id = org.id) SELECT name, depth FROM org ORDER BY depth, name;"),
            Task("l28-t2", "Find all employees under manager 'Owen Brooks' (exclude Owen himself). Show name, sorted by name.", "", "WITH RECURSIVE reports(id, name, manager_id) AS (SELECT id, name, manager_id FROM employees WHERE name = 'Owen Brooks' UNION ALL SELECT employees.id, employees.name, employees.manager_id FROM employees JOIN reports ON employees.manager_id = reports.id) SELECT name FROM reports WHERE name <> 'Owen Brooks' ORDER BY name;"),
            Task("l28-t3", "Build a management path for every employee (e.g., 'Rina Kapoor > Owen Brooks > Mei Lin'). Show name and path, sorted by path.", "", "WITH RECURSIVE org(id, name, manager_id, path) AS (SELECT id, name, manager_id, name FROM employees WHERE manager_id IS NULL UNION ALL SELECT employees.id, employees.name, employees.manager_id, org.path || ' > ' || employees.name FROM employees JOIN org ON employees.manager_id = org.id) SELECT name, path FROM org ORDER BY path;"),
            Task("l28-t4", "Walk customer referrals starting from 'Asha Rao' and show referral depth (0 for Asha). Show name and depth, sorted by depth.", "", "WITH RECURSIVE referrals(id, name, depth) AS (SELECT id, name, 0 FROM customers WHERE name = 'Asha Rao' UNION ALL SELECT customers.id, customers.name, referrals.depth + 1 FROM customers JOIN referrals ON customers.referrer_id = referrals.id) SELECT name, depth FROM referrals ORDER BY depth;"),
            Task("l28-t5", "Generate numbers 1 through 5 using a recursive CTE with column 'n'. Sort by n.", "", "WITH RECURSIVE numbers(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM numbers WHERE n < 5) SELECT n FROM numbers ORDER BY n;"),
        ]),
    Lesson("window-ranking", 23, "Window Ranking", ["ROW_NUMBER", "RANK", "PARTITION BY"], ["products", "customers", "orders", "order_items"], [
            Task("l24-t1", "Rank products by price from highest to lowest. Show name, price, and RANK() as 'price_rank', sorted by price_rank then name.", "", "SELECT name, price, RANK() OVER (ORDER BY price DESC) AS price_rank FROM products ORDER BY price_rank, name;"),
            Task("l24-t2", "Assign row numbers to products within each category, ordered by price descending then name. Show category, name, price, and ROW_NUMBER() as 'category_row'. Sort by category then category_row.", "", "SELECT category, name, price, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, name) AS category_row FROM products ORDER BY category, category_row;"),
            Task("l24-t3", "Rank customers by their non-cancelled spend. Show name, spend (rounded to 2 decimals), and RANK() as 'spend_rank'. Use a subquery to calculate spend first. Sort by spend_rank then name.", "", "SELECT name, ROUND(spend, 2) AS spend, RANK() OVER (ORDER BY spend DESC) AS spend_rank FROM (SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name) AS customer_spend ORDER BY spend_rank, name;"),
            Task("l24-t4", "For every order, number that customer's orders by date. Show customer_id, order id (as 'order_id'), ordered_at, and ROW_NUMBER() as 'customer_order_number'. Sort by customer_id then customer_order_number.", "", "SELECT customer_id, id AS order_id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS customer_order_number FROM orders ORDER BY customer_id, customer_order_number;"),
            Task("l24-t5", "Dense-rank product categories by average product price. Show category, average price (rounded to 2 decimals, as 'average_price'), and DENSE_RANK() as 'category_rank'. Sort by category_rank then category.", "", "SELECT category, ROUND(AVG(price), 2) AS average_price, DENSE_RANK() OVER (ORDER BY AVG(price) DESC) AS category_rank FROM products GROUP BY category ORDER BY category_rank, category;"),
        ]),
    Lesson("window-analytics", 24, "Running Totals and Moving Averages", ["SUM OVER", "AVG OVER"], ["orders", "order_items", "products"], [
            Task("l25-t1", "Show each order's total (as 'order_total') and running revenue (as 'running_revenue') by order date. Group by order, sort by ordered_at then id. Both values rounded to 2 decimals.", "", "SELECT orders.id, orders.ordered_at, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total, ROUND(SUM(SUM(order_items.quantity * order_items.unit_price)) OVER (ORDER BY orders.ordered_at, orders.id), 2) AS running_revenue FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY orders.id, orders.ordered_at ORDER BY orders.ordered_at, orders.id;"),
            Task("l25-t2", "Show each order's total (as 'order_total') and its percentage of all revenue (as 'pct_of_revenue'), both rounded to 2 decimals. Sort by order_id.", "", "SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS order_total, ROUND(100.0 * SUM(quantity * unit_price) / SUM(SUM(quantity * unit_price)) OVER (), 2) AS pct_of_revenue FROM order_items GROUP BY order_id ORDER BY order_id;"),
            Task("l25-t3", "Show each product's name, category, price, and the category average price (as 'category_avg_price', rounded to 2 decimals) using AVG OVER. Sort by category then name.", "", "SELECT name, category, price, ROUND(AVG(price) OVER (PARTITION BY category), 2) AS category_avg_price FROM products ORDER BY category, name;"),
            Task("l25-t4", "Show each order with the previous order date for the same customer using LAG. Show customer_id, order id (as 'order_id'), ordered_at, and previous_order_at. Sort by customer_id then ordered_at.", "", "SELECT customer_id, id AS order_id, ordered_at, LAG(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS previous_order_at FROM orders ORDER BY customer_id, ordered_at;"),
            Task("l25-t5", "Show each order with the next order date for the same customer using LEAD. Show customer_id, order id (as 'order_id'), ordered_at, and next_order_at. Sort by customer_id then ordered_at.", "", "SELECT customer_id, id AS order_id, ordered_at, LEAD(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS next_order_at FROM orders ORDER BY customer_id, ordered_at;"),
        ]),
    Lesson("top-n-per-group", 25, "Top N Per Group", ["ROW_NUMBER", "filter ranked rows"], ["products", "orders", "order_items"], [
            Task("l26-t1", "Find the most expensive product in each category. Use ROW_NUMBER in a subquery. Show category, name, and price, sorted by category.", "", "SELECT category, name, price FROM (SELECT category, name, price, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, name) AS rn FROM products) AS ranked WHERE rn = 1 ORDER BY category;"),
            Task("l26-t2", "Find the top two products by total units sold. Use ROW_NUMBER in a subquery. Show name and units_sold, sorted by units_sold descending then name.", "", "SELECT name, units_sold FROM (SELECT products.name, SUM(order_items.quantity) AS units_sold, ROW_NUMBER() OVER (ORDER BY SUM(order_items.quantity) DESC, products.name) AS rn FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name) AS ranked WHERE rn <= 2 ORDER BY units_sold DESC, name;"),
            Task("l26-t3", "Find each customer's latest order. Use ROW_NUMBER in a subquery. Show customer_id, order id (as 'order_id'), and ordered_at, sorted by customer_id.", "", "SELECT customer_id, id AS order_id, ordered_at FROM (SELECT customer_id, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at DESC, id DESC) AS rn FROM orders) AS ranked WHERE rn = 1 ORDER BY customer_id;"),
            Task("l26-t4", "Find the top product by revenue within each category. Use ROW_NUMBER in a subquery. Show category, name, and revenue (rounded to 2 decimals), sorted by category.", "", "SELECT category, name, ROUND(revenue, 2) AS revenue FROM (SELECT products.category, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue, ROW_NUMBER() OVER (PARTITION BY products.category ORDER BY SUM(order_items.quantity * order_items.unit_price) DESC, products.name) AS rn FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.category, products.name) AS ranked WHERE rn = 1 ORDER BY category;"),
            Task("l26-t5", "Find the two newest orders per channel. Use ROW_NUMBER in a subquery. Show channel, order id (as 'order_id'), and ordered_at, sorted by channel then ordered_at descending.", "", "SELECT channel, id AS order_id, ordered_at FROM (SELECT channel, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY channel ORDER BY ordered_at DESC, id DESC) AS rn FROM orders) AS ranked WHERE rn <= 2 ORDER BY channel, ordered_at DESC;"),
        ]),
    Lesson("execution-order", 26, "Query Order", ["WHERE", "GROUP BY", "HAVING", "ORDER BY"], ["orders", "order_items", "customers"], [
        Task("l12-t1", "For delivered orders only, show total revenue per order (as 'order_total', rounded to 2 decimals). Keep only orders with total above 100. Sort by order_total descending.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total FROM orders JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY orders.id HAVING SUM(order_items.quantity * order_items.unit_price) > 100 ORDER BY order_total DESC;"),
        Task("l12-t2", "By country, count delivered orders and keep countries with at least two. Show country and count as 'delivered_orders', sorted by delivered_orders descending then country.", "", "SELECT customers.country, COUNT(orders.id) AS delivered_orders FROM customers JOIN orders ON orders.customer_id = customers.id WHERE orders.status = 'delivered' GROUP BY customers.country HAVING COUNT(orders.id) >= 2 ORDER BY delivered_orders DESC, customers.country;"),
        Task("l12-t3", "Show each customer's total spending (as 'spend', rounded to 2 decimals) for non-cancelled orders, sorted by spend descending. Join customers, orders, and order_items.", "", "SELECT customers.name, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name ORDER BY spend DESC;"),
        Task("l12-t4", "Show order channels with average order total above 75 (as 'avg_total', rounded to 2 decimals). Use a subquery to calculate each order's total first. Sort by avg_total descending.", "", "SELECT orders.channel, ROUND(AVG(order_totals.total), 2) AS avg_total FROM orders JOIN (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) AS order_totals ON order_totals.order_id = orders.id GROUP BY orders.channel HAVING AVG(order_totals.total) > 75 ORDER BY avg_total DESC;"),
        Task("l12-t5", "Find active (not discontinued) product categories with more than one product in stock (stock > 0). Show category and count as 'stocked_products', sorted by category.", "", "SELECT category, COUNT(*) AS stocked_products FROM products WHERE discontinued = 0 AND stock > 0 GROUP BY category HAVING COUNT(*) > 1 ORDER BY category;"),
    ]),
    Lesson("indexes-query-plans", 27, "Indexes and Query Plans", ["CREATE INDEX", "EXPLAIN QUERY PLAN"], ["products", "orders", "customers", "order_items"], [
            Task("l34-t1", "Create an index named 'idx_orders_customer_id' on orders(customer_id).", "", "CREATE INDEX idx_orders_customer_id ON orders(customer_id);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_orders_customer_id';"),
            Task("l34-t2", "Create a composite index named 'idx_orders_status_ordered_at' on orders(status, ordered_at).", "", "CREATE INDEX idx_orders_status_ordered_at ON orders(status, ordered_at);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_orders_status_ordered_at';"),
            Task("l34-t3", "Create a unique index named 'idx_customers_name_city' on customers(name, city).", "", "CREATE UNIQUE INDEX idx_customers_name_city ON customers(name, city);", "SELECT name, \"unique\" FROM pragma_index_list('customers') WHERE name = 'idx_customers_name_city';"),
            Task("l34-t4", "Use EXPLAIN QUERY PLAN to see how SQLite resolves a customer lookup by id.", "", "EXPLAIN QUERY PLAN SELECT * FROM customers WHERE id = 1;"),
            Task("l34-t5", "Create an index named 'idx_order_items_product_id' on order_items(product_id) to speed up product joins.", "", "CREATE INDEX idx_order_items_product_id ON order_items(product_id);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_order_items_product_id';"),
        ]),
    Lesson("interview-filters", 28, "Interview Filtering Patterns", ["BETWEEN", "NOT IN", "multi-condition"], ["products", "customers", "orders"], [
            Task("l20-t1", "Find non-discontinued products priced between 25 and 90 inclusive. Show name and price, sorted by price then name.", "", "SELECT name, price FROM products WHERE price BETWEEN 25 AND 90 AND discontinued = 0 ORDER BY price, name;"),
            Task("l20-t2", "Find customers who are not bronze tier and signed up on or after March 2023. Show name, tier, and signup_date, sorted by signup_date then name.", "", "SELECT name, tier, signup_date FROM customers WHERE tier <> 'bronze' AND signup_date >= '2023-03-01' ORDER BY signup_date, name;"),
            Task("l20-t3", "Find non-cancelled orders placed through web or mobile. Show id, status, and channel, sorted by id.", "", "SELECT id, status, channel FROM orders WHERE status <> 'cancelled' AND channel IN ('web', 'mobile') ORDER BY id;"),
            Task("l20-t4", "Find products whose name contains 'Desk' or whose category is 'Office'. Show name and category, sorted by name.", "", "SELECT name, category FROM products WHERE name LIKE '%Desk%' OR category = 'Office' ORDER BY name;"),
            Task("l20-t5", "Find gold-tier customers from India or Singapore. Show name, country, and tier, sorted by name.", "", "SELECT name, country, tier FROM customers WHERE tier = 'gold' AND country IN ('India', 'Singapore') ORDER BY name;"),
        ]),
    Lesson("insert", 29, "INSERT Rows", ["INSERT"], ["products", "customers", "orders", "order_items"], [
        Task("l13-t1", "Insert a new Office product with id 13, named 'Cable Clips', priced 7.50, stock 90, rating 4.2, not discontinued.", "", "INSERT INTO products (id, name, category, price, stock, rating, discontinued) VALUES (13, 'Cable Clips', 'Office', 7.50, 90, 4.2, 0);", "SELECT name, category, price, stock, rating, discontinued FROM products WHERE id = 13;"),
        Task("l13-t2", "Insert a new customer with id 9, named 'Hana Lee', from Seoul, South Korea, signed up on 2024-04-15, bronze tier, no referrer.", "", "INSERT INTO customers (id, name, city, country, signup_date, tier, referrer_id) VALUES (9, 'Hana Lee', 'Seoul', 'South Korea', '2024-04-15', 'bronze', NULL);", "SELECT name, city, country, signup_date, tier, referrer_id FROM customers WHERE id = 9;"),
        Task("l13-t3", "Insert a new order with id 111 for customer 1, ordered on 2024-04-16, status processing, channel web.", "", "INSERT INTO orders (id, customer_id, ordered_at, status, channel) VALUES (111, 1, '2024-04-16', 'processing', 'web');", "SELECT id, customer_id, ordered_at, status, channel FROM orders WHERE id = 111;"),
        Task("l13-t4", "Insert two order items for order 101: id 1018 for product 2 quantity 1 at 42.50, and id 1019 for product 5 quantity 2 at 12.75.", "", "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (1018, 101, 2, 1, 42.50), (1019, 101, 5, 2, 12.75);", "SELECT order_id, product_id, quantity, unit_price FROM order_items WHERE id IN (1018, 1019) ORDER BY product_id;"),
    ]),
    Lesson("update", 30, "UPDATE Rows", ["UPDATE", "SET"], ["products", "orders", "support_tickets"], [
        Task("l14-t1", "Mark product 12 as active (discontinued = 0) and set its stock to 25.", "", "UPDATE products SET discontinued = 0, stock = 25 WHERE id = 12;", "SELECT stock, discontinued FROM products WHERE id = 12;"),
        Task("l14-t2", "Increase all Office product prices by 2.00.", "", "UPDATE products SET price = price + 2.00 WHERE category = 'Office';", "SELECT name, price FROM products WHERE category = 'Office' ORDER BY name;"),
        Task("l14-t3", "Change order 105 status to 'shipped'.", "", "UPDATE orders SET status = 'shipped' WHERE id = 105;", "SELECT id, status FROM orders WHERE id = 105;"),
        Task("l14-t4", "Close all open high-priority support tickets and set their resolved_at to '2024-04-10'.", "", "UPDATE support_tickets SET status = 'closed', resolved_at = '2024-04-10' WHERE status = 'open' AND priority = 'high';", "SELECT id, priority, status, resolved_at FROM support_tickets WHERE priority = 'high' ORDER BY id;"),
    ]),
    Lesson("delete", 31, "DELETE Rows", ["DELETE"], ["products", "orders", "support_tickets"], [
        Task("l15-t1", "Delete only discontinued products that have zero stock.", "", "DELETE FROM products WHERE discontinued = 1 AND stock = 0;", "SELECT id, name FROM products ORDER BY id;"),
        Task("l15-t2", "Delete cancelled order 103: first delete its support ticket, then its order items, then the order itself.", "", "DELETE FROM support_tickets WHERE order_id = 103; DELETE FROM order_items WHERE order_id = 103; DELETE FROM orders WHERE id = 103 AND status = 'cancelled';", "SELECT id FROM orders WHERE id = 103 UNION ALL SELECT order_id FROM order_items WHERE order_id = 103 UNION ALL SELECT order_id FROM support_tickets WHERE order_id = 103;"),
        Task("l15-t3", "Delete closed low-priority support tickets.", "", "DELETE FROM support_tickets WHERE status = 'closed' AND priority = 'low';", "SELECT id, priority, status FROM support_tickets ORDER BY id;"),
        Task("l15-t4", "Delete order items for Fitness products with rating below 4.0, then delete those products.", "", "DELETE FROM order_items WHERE product_id IN (SELECT id FROM products WHERE category = 'Fitness' AND rating < 4.0); DELETE FROM products WHERE category = 'Fitness' AND rating < 4.0;", "SELECT id, name, category, rating FROM products ORDER BY id;"),
    ]),
    Lesson("create-table", 32, "CREATE TABLE", ["CREATE TABLE", "types"], ["products"], [
        Task("l16-t1", "Create a suppliers table with columns: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), country (TEXT NOT NULL), and active (INTEGER NOT NULL DEFAULT 1).", "", "CREATE TABLE suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);", "SELECT name, type, \"notnull\", dflt_value, pk FROM pragma_table_info('suppliers') ORDER BY cid;"),
        Task("l16-t2", "Create a product_reviews table with: id (INTEGER PRIMARY KEY), product_id (INTEGER NOT NULL, FK to products), rating (INTEGER NOT NULL), and comment (TEXT, nullable).", "", "CREATE TABLE product_reviews (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), rating INTEGER NOT NULL, comment TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('product_reviews') ORDER BY cid;"),
        Task("l16-t3", "Create a coupons table with: id (INTEGER PRIMARY KEY), code (TEXT NOT NULL UNIQUE), percent_off (INTEGER NOT NULL), and expires_at (TEXT, nullable).", "", "CREATE TABLE coupons (id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, percent_off INTEGER NOT NULL, expires_at TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('coupons') ORDER BY cid;"),
        Task("l16-t4", "Create an inventory_audits table with: id (INTEGER PRIMARY KEY), product_id (INTEGER NOT NULL, FK to products), counted_at (TEXT NOT NULL), counted_stock (INTEGER NOT NULL), and note (TEXT, nullable).", "", "CREATE TABLE inventory_audits (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), counted_at TEXT NOT NULL, counted_stock INTEGER NOT NULL, note TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('inventory_audits') ORDER BY cid;"),
    ]),
    Lesson("alter-table", 33, "ALTER TABLE", ["ALTER TABLE"], ["products", "customers"], [
        Task("l17-t1", "Add a reorder_level INTEGER NOT NULL column to products with default 10.", "", "ALTER TABLE products ADD COLUMN reorder_level INTEGER NOT NULL DEFAULT 10;", "SELECT name, type, \"notnull\", dflt_value FROM pragma_table_info('products') WHERE name = 'reorder_level';"),
        Task("l17-t2", "Add a marketing_opt_in INTEGER NOT NULL column to customers with default 0.", "", "ALTER TABLE customers ADD COLUMN marketing_opt_in INTEGER NOT NULL DEFAULT 0;", "SELECT name, type, \"notnull\", dflt_value FROM pragma_table_info('customers') WHERE name = 'marketing_opt_in';"),
        Task("l17-t3", "Rename the support_tickets table to helpdesk_tickets.", "", "ALTER TABLE support_tickets RENAME TO helpdesk_tickets;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('support_tickets', 'helpdesk_tickets') ORDER BY name;"),
        Task("l17-t4", "Rename the products 'stock' column to 'units_in_stock'.", "", "ALTER TABLE products RENAME COLUMN stock TO units_in_stock;", "SELECT name FROM pragma_table_info('products') WHERE name IN ('stock', 'units_in_stock') ORDER BY name;"),
    ]),
    Lesson("drop-table", 34, "DROP TABLE", ["DROP TABLE", "IF EXISTS"], ["support_tickets", "shipments"], [
        Task("l18-t1", "Drop the support_tickets table.", "", "DROP TABLE support_tickets;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'support_tickets';"),
        Task("l18-t2", "Drop the shipments table only if it exists.", "", "DROP TABLE IF EXISTS shipments;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'shipments';"),
        Task("l18-t3", "Create a table named scratch with columns id (INTEGER PRIMARY KEY) and note (TEXT), then drop it.", "", "CREATE TABLE scratch (id INTEGER PRIMARY KEY, note TEXT); DROP TABLE scratch;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'scratch';"),
        Task("l18-t4", "Drop the order_items table.", "", "DROP TABLE order_items;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'order_items';"),
    ]),
    Lesson("leetcode-patterns", 35, "Classic Interview Patterns", ["second highest", "duplicates", "gaps"], ["products", "customers", "orders"], [
            Task("l32-t1", "Find the second most expensive product price (as 'second_highest_price'). Use a subquery.", "", "SELECT MAX(price) AS second_highest_price FROM products WHERE price < (SELECT MAX(price) FROM products);"),
            Task("l32-t2", "Find countries that have more than one customer. Show country and count as 'customer_count', sorted by country.", "", "SELECT country, COUNT(*) AS customer_count FROM customers GROUP BY country HAVING COUNT(*) > 1 ORDER BY country;"),
            Task("l32-t3", "Find customers with consecutive orders less than 40 days apart. Use LAG to get previous_order_at. Show distinct name, sorted by name.", "", "SELECT DISTINCT name FROM (SELECT customers.name, ordered_at, LAG(ordered_at) OVER (PARTITION BY customers.id ORDER BY ordered_at) AS previous_order_at FROM customers JOIN orders ON orders.customer_id = customers.id) AS ordered WHERE previous_order_at IS NOT NULL AND julianday(ordered_at) - julianday(previous_order_at) < 40 ORDER BY name;"),
            Task("l32-t4", "Find product pairs in the same category with the same rounded rating (ROUND to 0 decimals, a.id < b.id). Show product_a, product_b, category, and rating. Sort by category then product_a.", "", "SELECT a.name AS product_a, b.name AS product_b, a.category, a.rating FROM products a JOIN products b ON a.category = b.category AND a.id < b.id AND ROUND(a.rating, 0) = ROUND(b.rating, 0) ORDER BY a.category, product_a;"),
            Task("l32-t5", "Return the first order for every customer who has ordered. Use ROW_NUMBER in a subquery. Show customer_id, first_order_id, and ordered_at, sorted by customer_id.", "", "SELECT customer_id, id AS first_order_id, ordered_at FROM (SELECT customer_id, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS rn FROM orders) AS ranked WHERE rn = 1 ORDER BY customer_id;"),
        ]),
    Lesson("business-analytics", 36, "Business Intelligence SQL", ["JOIN", "arithmetic", "business-logic"], ["customers", "orders", "order_items", "products", "shipments"], [
            Task("l36-t1", "Calculate the total revenue (quantity × unit_price) per customer city. Show city and 'total_revenue' (rounded to 2 decimals), sorted by total_revenue descending.", "", "SELECT customers.city, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS total_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.city ORDER BY total_revenue DESC;"),
            Task("l36-t2", "For delivered orders, show the order id and the 'net_amount' (sum of item revenue + shipping_cost). Sort by net_amount descending.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price) + shipments.shipping_cost, 2) AS net_amount FROM orders JOIN order_items ON order_items.order_id = orders.id JOIN shipments ON shipments.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY orders.id, shipments.shipping_cost ORDER BY net_amount DESC;"),
            Task("l36-t3", "Find the average discount per product category. Discount is (products.price - order_items.unit_price). Show category and 'avg_discount' (rounded to 2 decimals), sorted by avg_discount descending.", "", "SELECT products.category, ROUND(AVG(products.price - order_items.unit_price), 2) AS avg_discount FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.category ORDER BY avg_discount DESC;"),
            Task("l36-t4", "Calculate each customer's 'loyalty_points': 5 points per item purchased + 1 point for every 10 currency spent. Show name and 'points' (as integer), sorted by points descending.", "", "SELECT customers.name, CAST(SUM(order_items.quantity) * 5 + SUM(order_items.quantity * order_items.unit_price) / 10 AS INTEGER) AS points FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name ORDER BY points DESC;"),
            Task("l36-t5", "For each category, show 'inventory_value' (sum of stock × price) and 'actual_revenue' (sum of items). Use a LEFT JOIN on order_items to include categories with no sales. Sort by category.", "", "SELECT products.category, ROUND(SUM(products.stock * products.price), 2) AS inventory_value, ROUND(COALESCE(SUM(order_items.quantity * order_items.unit_price), 0), 2) AS actual_revenue FROM products LEFT JOIN order_items ON order_items.product_id = products.id GROUP BY products.category ORDER BY products.category;"),
            Task("l36-t6", "Find the Average Order Value (AOV) for each customer tier. AOV is total revenue divided by unique order count. Show tier and 'avg_order_value' (rounded to 2 decimals), sorted by avg_order_value descending.", "", "SELECT customers.tier, ROUND(SUM(order_items.quantity * order_items.unit_price) / CAST(COUNT(DISTINCT orders.id) AS REAL), 2) AS avg_order_value FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.tier ORDER BY avg_order_value DESC;"),
            Task("l36-t7", "Calculate 'carrier_cost_per_unit': for each carrier, find the total shipping cost divided by total quantity of items delivered. Show carrier and 'cost_per_unit' (rounded to 2 decimals), sorted by cost_per_unit.", "", "SELECT shipments.carrier, ROUND(SUM(shipments.shipping_cost) / SUM(order_items.quantity), 2) AS cost_per_unit FROM shipments JOIN order_items ON order_items.order_id = shipments.order_id GROUP BY shipments.carrier ORDER BY cost_per_unit;"),
            Task("l36-t8", "Find 'top_rated_revenue' products: those with a rating above 4.5 and total revenue exceeding 150. Show name, rating, and revenue, sorted by revenue descending.", "", "SELECT products.name, products.rating, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id WHERE products.rating > 4.5 GROUP BY products.id, products.name, products.rating HAVING revenue > 150 ORDER BY revenue DESC;"),
            Task("l36-t9", "Calculate 'referral_revenue': for each customer who referred someone, find the total revenue generated by their referrals. Show referrer name and 'referral_revenue', sorted by referral_revenue descending.", "", "SELECT r.name, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS referral_revenue FROM customers r JOIN customers c ON c.referrer_id = r.id JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id GROUP BY r.id, r.name ORDER BY referral_revenue DESC;"),
            Task("l36-t10", "Show 'stock_to_sales_ratio': for each product, show stock divided by total units sold. Show name, stock, and 'ratio' (rounded to 2 decimals), sorted by ratio descending.", "", "SELECT products.name, products.stock, ROUND(CAST(products.stock AS REAL) / SUM(order_items.quantity), 2) AS ratio FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name, products.stock ORDER BY ratio DESC;"),
        ]),
    Lesson("final-interview-sets", 37, "Final Interview Sets", ["multi-step", "analytics", "business SQL"], ["customers", "orders", "order_items", "products", "shipments", "support_tickets"], [
            Task("l35-t1", "Find the top three customers by delivered revenue (only delivered orders). Show customer name and delivered_revenue (rounded to 2 decimals), sorted by delivered_revenue descending. Use LIMIT 3.", "", "SELECT customers.name, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS delivered_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY customers.id, customers.name ORDER BY delivered_revenue DESC LIMIT 3;"),
            Task("l35-t2", "For each month, show total orders (as 'orders_count'), total revenue, and count of delivered orders (as 'delivered_orders'). Use substr for month. Sort by month.", "", "SELECT substr(orders.ordered_at, 1, 7) AS month, COUNT(DISTINCT orders.id) AS orders_count, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS revenue, COUNT(DISTINCT CASE WHEN orders.status = 'delivered' THEN orders.id END) AS delivered_orders FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY month ORDER BY month;"),
            Task("l35-t3", "Find products with above-average product revenue. Use a CTE 'product_revenue'. Show name and revenue (rounded to 2 decimals), sorted by revenue descending.", "", "WITH product_revenue AS (SELECT products.id, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name) SELECT name, ROUND(revenue, 2) AS revenue FROM product_revenue WHERE revenue > (SELECT AVG(revenue) FROM product_revenue) ORDER BY revenue DESC;"),
            Task("l35-t4", "Find customers who have both a support ticket and delivered revenue above 100. Use a CTE 'delivered_spend' and EXISTS. Show name and spend (rounded to 2 decimals), sorted by spend descending.", "", "WITH delivered_spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY customers.id, customers.name) SELECT name, ROUND(spend, 2) AS spend FROM delivered_spend WHERE spend > 100 AND EXISTS (SELECT 1 FROM support_tickets WHERE support_tickets.customer_id = delivered_spend.id) ORDER BY spend DESC;"),
            Task("l35-t5", "Build an operations dashboard by order: show order id, order_total (rounded to 2 decimals), shipment_state ('delivered'/'in_transit'/'not_shipped'), and ticket_count. Use LEFT JOINs for shipments and support_tickets. Sort by order id.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total, CASE WHEN shipments.delivered_at IS NOT NULL THEN 'delivered' WHEN shipments.shipped_at IS NOT NULL THEN 'in_transit' ELSE 'not_shipped' END AS shipment_state, COUNT(DISTINCT support_tickets.id) AS ticket_count FROM orders JOIN order_items ON order_items.order_id = orders.id LEFT JOIN shipments ON shipments.order_id = orders.id LEFT JOIN support_tickets ON support_tickets.order_id = orders.id GROUP BY orders.id, shipments.delivered_at, shipments.shipped_at ORDER BY orders.id;"),
        ]),
]


NOTES_BY_LESSON = {
    "select-columns": "https://www.w3schools.com/sql/sql_select.asp",
    "where-numeric": "https://www.w3schools.com/sql/sql_where.asp",
    "where-text": "https://www.w3schools.com/sql/sql_like.asp",
    "sorting-limits": "https://www.w3schools.com/sql/sql_orderby.asp",
    "select-review": "https://www.w3schools.com/sql/sql_operators.asp",
    "inner-joins": "https://www.w3schools.com/sql/sql_join_inner.asp",
    "outer-joins": "https://www.w3schools.com/sql/sql_join_left.asp",
    "nulls": "https://www.w3schools.com/sql/sql_null_values.asp",
    "expressions": "https://www.w3schools.com/sql/sql_case.asp",
    "aggregates": "https://www.w3schools.com/sql/sql_count_avg_sum.asp",
    "grouping": "https://www.w3schools.com/sql/sql_groupby.asp",
    "execution-order": "https://www.w3schools.com/sql/sql_having.asp",
    "insert": "https://www.w3schools.com/sql/sql_insert.asp",
    "update": "https://www.w3schools.com/sql/sql_update.asp",
    "delete": "https://www.w3schools.com/sql/sql_delete.asp",
    "create-table": "https://www.w3schools.com/sql/sql_create_table.asp",
    "alter-table": "https://www.w3schools.com/sql/sql_alter.asp",
    "drop-table": "https://www.w3schools.com/sql/sql_drop_table.asp",
    "union-intersect-except": "https://www.w3schools.com/sql/sql_union.asp",
    "advanced-review": "https://www.w3schools.com/sql/sql_any_all.asp",
    "interview-filters": "https://www.w3schools.com/sql/sql_between.asp",
    "string-functions": "https://www.sqlite.org/lang_corefunc.html",
    "date-analytics": "https://www.sqlite.org/lang_datefunc.html",
    "conditional-aggregation": "https://www.w3schools.com/sql/sql_case.asp",
    "window-ranking": "https://www.postgresql.org/docs/current/tutorial-window.html",
    "window-analytics": "https://www.postgresql.org/docs/current/functions-window.html",
    "top-n-per-group": "https://www.postgresql.org/docs/current/tutorial-window.html",
    "ctes": "https://www.sqlite.org/lang_with.html",
    "recursive-ctes": "https://www.sqlite.org/lang_with.html",
    "semi-anti-joins": "https://www.w3schools.com/sql/sql_exists.asp",
    "self-joins": "https://www.w3schools.com/sql/sql_join_self.asp",
    "set-operations-advanced": "https://www.w3schools.com/sql/sql_union.asp",
    "leetcode-patterns": "https://www.postgresql.org/docs/current/tutorial-window.html",
    "data-cleaning": "https://www.sqlite.org/lang_corefunc.html",
    "indexes-query-plans": "https://www.sqlite.org/eqp.html",
    "final-interview-sets": "https://www.w3schools.com/sql/",
}


LESSON_BY_ID = {lesson.id: lesson for lesson in LESSONS}
KNOWN_TABLES = tuple(SEED.keys())


def lesson_index() -> list[dict[str, Any]]:
    return [
        {
            "id": lesson.id,
            "number": lesson.number,
            "title": lesson.title,
            "focus": lesson.focus,
            "taskCount": len(lesson.tasks),
            "notesUrl": NOTES_BY_LESSON.get(lesson.id, ""),
        }
        for lesson in LESSONS
    ]


def lesson_payload(lesson_id: str) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    return {
        "id": lesson.id,
        "number": lesson.number,
        "title": lesson.title,
        "focus": lesson.focus,
        "notesUrl": NOTES_BY_LESSON.get(lesson.id, ""),
        "tables": preview_tables(lesson.tables),
        "tasks": [
            {
                "id": task.id,
                "prompt": task.prompt,
                "starter": task.starter,
                "hint": task.hint,
                "tableNames": task_table_names(task, lesson.tables),
                "tables": preview_tables(task_table_names(task, lesson.tables)),
            }
            for task in lesson.tasks
        ],
    }


def get_lesson(lesson_id: str) -> Lesson:
    if lesson_id in LESSON_BY_ID:
        return LESSON_BY_ID[lesson_id]
    return LESSONS[0]


def get_task(lesson: Lesson, task_id: str) -> Task:
    for task in lesson.tasks:
        if task.id == task_id:
            return task
    return lesson.tasks[0]


def build_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)", SEED["products"])
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?)", SEED["customers"])
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", SEED["orders"])
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", SEED["order_items"])
    conn.executemany("INSERT INTO shipments VALUES (?, ?, ?, ?, ?, ?)", SEED["shipments"])
    conn.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?)", SEED["employees"])
    conn.executemany("INSERT INTO support_tickets VALUES (?, ?, ?, ?, ?, ?, ?)", SEED["support_tickets"])
    conn.commit()
    return conn


def preview_tables(table_names: list[str]) -> list[dict[str, Any]]:
    conn = build_connection()
    try:
        return [query_table_preview(conn, name) for name in table_names]
    finally:
        conn.close()


def task_table_names(task: Task, fallback: list[str]) -> list[str]:
    text = "\n".join(
        value
        for value in (task.prompt, task.starter, task.solution, task.verifier or "")
        if value
    ).lower()
    names = [
        table_name
        for table_name in KNOWN_TABLES
        if re.search(rf"\b{re.escape(table_name)}\b", text)
    ]
    return names or fallback


def query_table_preview(conn: sqlite3.Connection, table_name: str) -> dict[str, Any]:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({quote_identifier(table_name)})")]
    rows = [
        [normalize_value(row[column]) for column in columns]
        for row in conn.execute(f"SELECT * FROM {quote_identifier(table_name)} LIMIT 8")
    ]
    total = conn.execute(f"SELECT COUNT(*) AS count FROM {quote_identifier(table_name)}").fetchone()["count"]
    return {"name": table_name, "columns": columns, "rows": rows, "total": total}


def run_sql(lesson_id: str, sql: str) -> dict[str, Any]:
    get_lesson(lesson_id)
    conn = build_connection()
    try:
        return execute_sql(conn, sql)
    finally:
        conn.close()


def check_sql(lesson_id: str, task_id: str, sql: str) -> dict[str, Any]:
    lesson = get_lesson(lesson_id)
    task = get_task(lesson, task_id)

    expected_conn = build_connection()
    user_conn = build_connection()
    try:
        execute_sql(expected_conn, task.solution)
        expected = query_result(expected_conn, task.verifier) if task.verifier else execute_sql(expected_conn, task.solution)

        user_run = execute_sql(user_conn, sql)
        actual = query_result(user_conn, task.verifier) if task.verifier else user_run

        order_sensitive = task_requires_order(task)
        correct = comparable(actual, order_sensitive) == comparable(
            expected, order_sensitive
        )
        return {
            "correct": correct,
            "message": "Solved."
            if correct
            else (
                "Not quite. This task asks for a specific order, so compare columns, row values, and ordering."
                if order_sensitive
                else "Not quite. Compare your columns, filters, and row values."
            ),
            "orderSensitive": order_sensitive,
            "result": actual,
            "expected": expected if not correct else None,
            "solution": task.solution,
        }
    finally:
        expected_conn.close()
        user_conn.close()


def execute_sql(conn: sqlite3.Connection, sql: str) -> dict[str, Any]:
    statements = split_sql(sql)
    if not statements:
        raise ValueError("Write a SQL statement first.")

    validate_statements(statements)
    final_statement = statements[-1]
    prior = statements[:-1]

    if prior:
        conn.executescript(";\n".join(prior) + ";")

    if is_result_statement(final_statement):
        return query_result(conn, final_statement)

    conn.executescript(final_statement + ";")
    conn.commit()
    return {"columns": [], "rows": [], "rowCount": 0, "message": "Statement executed."}


def query_result(conn: sqlite3.Connection, statement: str | None) -> dict[str, Any]:
    if not statement:
        return {"columns": [], "rows": [], "rowCount": 0}
    cursor = conn.execute(statement)
    rows = cursor.fetchmany(MAX_ROWS + 1)
    columns = [description[0] for description in cursor.description or []]
    limited = rows[:MAX_ROWS]
    return {
        "columns": columns,
        "rows": [[normalize_value(row[column]) for column in columns] for row in limited],
        "rowCount": len(limited),
        "truncated": len(rows) > MAX_ROWS,
    }


def split_sql(sql: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False

    for char in sql:
        if quote:
            current.append(char)
            if char == quote and not escaped:
                quote = None
            escaped = char == "\\" and not escaped
            continue

        if char in ("'", '"'):
            quote = char
            current.append(char)
        elif char == ";":
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
        else:
            current.append(char)

    statement = "".join(current).strip()
    if statement:
        statements.append(statement)
    return [strip_sql_comments(statement).strip() for statement in statements if strip_sql_comments(statement).strip()]


def strip_sql_comments(statement: str) -> str:
    lines = []
    for line in statement.splitlines():
        marker = line.find("--")
        lines.append(line if marker == -1 else line[:marker])
    return "\n".join(lines)


def validate_statements(statements: list[str]) -> None:
    blocked = {
        "ATTACH",
        "DETACH",
        "VACUUM",
        "PRAGMA",
        "REINDEX",
        "ANALYZE",
    }
    for statement in statements:
        first = statement.lstrip().split(None, 1)[0].upper() if statement.strip() else ""
        if first in blocked:
            raise ValueError(f"{first} is not available in the practice sandbox.")


def is_result_statement(statement: str) -> bool:
    first = statement.lstrip().split(None, 1)[0].upper()
    return first in {"SELECT", "WITH", "VALUES", "EXPLAIN"}


def comparable(
    result: dict[str, Any], order_sensitive: bool
) -> tuple[tuple[str, ...], tuple[tuple[Any, ...], ...]]:
    rows = [tuple(row) for row in result.get("rows", [])]
    if not order_sensitive:
        rows = sorted(rows, key=lambda row: json.dumps(row, sort_keys=True, default=str))
    return (
        tuple(result.get("columns", [])),
        tuple(rows),
    )


def task_requires_order(task: Task) -> bool:
    return bool(
        re.search(
            r"\b(alphabetically|ascending|descending|sorted|sort|ordered|order by|newest|oldest|highest|lowest|cheapest|expensive|top|latest|first|rank|row number|running|previous|next|calendar month|quarter)\b",
            task.prompt,
            re.IGNORECASE,
        )
    )


def normalize_value(value: Any) -> Any:
    if isinstance(value, float):
        return round(value, 4)
    return value


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'
