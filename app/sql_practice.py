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
    Lesson("basic-capstone", 6, "Basic Queries: Interview Capstone", ["Hint-Free", "Filtering"], ["customers", "orders", "products"], [
        Task("bc-t1", "Retrieve all product names and their current stock levels.", "", "SELECT name, stock FROM products;"),
        Task("bc-t2", "Find the email addresses of customers who live in 'Canada'.", "", "SELECT email FROM customers WHERE country = 'Canada';"),
        Task("bc-t3", "List all products that cost exactly 19.99.", "", "SELECT * FROM products WHERE price = 19.99;"),
        Task("bc-t4", "Identify orders that have a status of 'pending'. Return the order IDs.", "", "SELECT id FROM orders WHERE status = 'pending';"),
        Task("bc-t5", "Find products with a stock level of 0. Return the product name.", "", "SELECT name FROM products WHERE stock = 0;"),
        Task("bc-t6", "List the top 5 most expensive products. Return name and price.", "", "SELECT name, price FROM products ORDER BY price DESC LIMIT 5;"),
        Task("bc-t7", "Find all customers whose name starts with the letter 'J'. Return their names.", "", "SELECT name FROM customers WHERE name LIKE 'J%';"),
        Task("bc-t8", "Retrieve products priced between 50 and 100 inclusive. Return name and price.", "", "SELECT name, price FROM products WHERE price BETWEEN 50 AND 100;"),
        Task("bc-t9", "Identify customers from either 'USA' or 'UK'. Return name and country.", "", "SELECT name, country FROM customers WHERE country IN ('USA', 'UK');"),
        Task("bc-t10", "Find orders placed before January 15, 2024. Return order id and ordered_at.", "", "SELECT id, ordered_at FROM orders WHERE ordered_at < '2024-01-15 00:00:00';"),
        Task("bc-t11", "Retrieve the 3 oldest customers based on registration date (assuming id represents chronological order). Return name and id.", "", "SELECT name, id FROM customers ORDER BY id ASC LIMIT 3;"),
        Task("bc-t12", "List all products that belong to the 'Electronics' category and cost more than 500.", "", "SELECT * FROM products WHERE category = 'Electronics' AND price > 500;"),
        Task("bc-t13", "Find customers who do not have a referrer (referrer_id is null). Return name.", "", "SELECT name FROM customers WHERE referrer_id IS NULL;"),
        Task("bc-t14", "Identify products whose name contains the word 'Pro'. Return name.", "", "SELECT name FROM products WHERE name LIKE '%Pro%';"),
        Task("bc-t15", "Retrieve the second page of 5 products when ordered alphabetically by name (i.e. skip the first 5).", "", "SELECT * FROM products ORDER BY name ASC LIMIT 5 OFFSET 5;"),
        Task("bc-t16", "Find orders that are NOT in 'shipped' or 'delivered' status.", "", "SELECT * FROM orders WHERE status NOT IN ('shipped', 'delivered');"),
        Task("bc-t17", "List product categories available in the store without any duplicates. Return category.", "", "SELECT DISTINCT category FROM products;"),
        Task("bc-t18", "Find products where the stock is dangerously low (less than 10) but not completely out. Return name and stock.", "", "SELECT name, stock FROM products WHERE stock > 0 AND stock < 10;"),
        Task("bc-t19", "Identify customers whose email address ends with '@example.com'. Return name and email.", "", "SELECT name, email FROM customers WHERE email LIKE '%@example.com';"),
        Task("bc-t20", "List all orders sorted chronologically by order date, newest first.", "", "SELECT * FROM orders ORDER BY ordered_at DESC;"),
    ]),
    Lesson("inner-joins", 7, "INNER JOINs", ["JOIN", "ON"], ["orders", "customers", "order_items", "products"], [
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
    Lesson("outer-joins", 8, "LEFT JOINs", ["LEFT JOIN", "missing rows"], ["products", "order_items", "orders", "shipments"], [
        Task("l7-t1", "Show every product name and any order item id (as 'item_id') that references it, sorted by product name", "", "SELECT products.name, order_items.id AS item_id FROM products LEFT JOIN order_items ON order_items.product_id = products.id ORDER BY products.name;"),
        Task("l7-t2", "Find products that have never been ordered. Show name, sorted by name", "", "SELECT products.name FROM products LEFT JOIN order_items ON order_items.product_id = products.id WHERE order_items.id IS NULL ORDER BY products.name;"),
        Task("l7-t3", "Show every order's id, status, and delivered_at from shipments (NULL if no shipment), sorted by order id", "", "SELECT orders.id, orders.status, shipments.delivered_at FROM orders LEFT JOIN shipments ON shipments.order_id = orders.id ORDER BY orders.id;"),
        Task("l7-t4", "Find orders with no shipment row. Show id and status, sorted by id", "", "SELECT orders.id, orders.status FROM orders LEFT JOIN shipments ON shipments.order_id = orders.id WHERE shipments.id IS NULL ORDER BY orders.id;"),
        Task("l7-t5", "Find customers who have NEVER placed an order. Show name, sorted by name.", "", "SELECT customers.name FROM customers LEFT JOIN orders ON orders.customer_id = customers.id WHERE orders.id IS NULL ORDER BY customers.name;"),
    ]),
    Lesson("right-joins", 9, "RIGHT JOINs", ["RIGHT JOIN", "driving tables"], ["order_items", "products"], [
        Task("l8r-t1", "Show every product name and any order item id (as 'item_id') that references it. Sort by product name.", "", "SELECT products.name, order_items.id AS item_id FROM order_items RIGHT JOIN products ON products.id = order_items.product_id ORDER BY products.name;"),
        Task("l8r-t2", "Find products that have never been ordered. Show name, sorted by name.", "", "SELECT products.name FROM order_items RIGHT JOIN products ON products.id = order_items.product_id WHERE order_items.id IS NULL ORDER BY products.name;"),
        Task("l8r-t3", "Show all employees and their manager's name (as 'manager'). Sort by employee name.", "", "SELECT e.name, m.name AS manager FROM employees m RIGHT JOIN employees e ON e.manager_id = m.id ORDER BY e.name;"),
        Task("l8r-t4", "Count how many order items exist for each product. Show product name and 'item_count', sorted by item_count descending.", "", "SELECT products.name, COUNT(order_items.id) AS item_count FROM order_items RIGHT JOIN products ON products.id = order_items.product_id GROUP BY products.id, products.name ORDER BY item_count DESC;"),
        Task("l8r-t5", "Find customers with no support tickets. Support tickets on the left, customers on the right. Show customer name, sorted by name.", "", "SELECT customers.name FROM support_tickets RIGHT JOIN customers ON customers.id = support_tickets.customer_id WHERE support_tickets.id IS NULL ORDER BY customers.name;"),
    ]),
    Lesson("full-joins", 10, "FULL JOINs", ["FULL OUTER JOIN", "mismatches"], ["customers", "orders", "shipments"], [
        Task("l9f-t1", "Show all customers and all orders. If a customer has no orders, or an order has no matching customer (due to bad data), show them anyway. Select customer name and order id, sorted by customer name", "", "SELECT customers.name, orders.id FROM customers FULL JOIN orders ON orders.customer_id = customers.id ORDER BY customers.name;"),
        Task("l9f-t2", "Find completely unmatched records: customers without orders AND orders without matching customers. Show customer name and order id. Sort by order id", "", "SELECT customers.name, orders.id FROM customers FULL JOIN orders ON orders.customer_id = customers.id WHERE customers.id IS NULL OR orders.id IS NULL ORDER BY orders.id;"),
        Task("l9f-t3", "Show all orders and all shipments together. Return order id, shipment id, and status, sorted by order id", "", "SELECT orders.id, shipments.id, orders.status FROM orders FULL JOIN shipments ON shipments.order_id = orders.id ORDER BY orders.id;"),
        Task("l9f-t4", "Find shipments that have no corresponding order, OR orders that have no corresponding shipment. Show order id and shipment id, sorted by order id.", "", "SELECT orders.id, shipments.id FROM orders FULL JOIN shipments ON shipments.order_id = orders.id WHERE orders.id IS NULL OR shipments.id IS NULL ORDER BY orders.id;"),
        Task("l9f-t5", "List all employees and all support tickets. This makes no logical sense but do it anyway (match on employee id = ticket id). Show employee name and ticket id, sorted by employee name.", "", "SELECT employees.name, support_tickets.id FROM employees FULL JOIN support_tickets ON support_tickets.id = employees.id ORDER BY employees.name;"),
    ]),
    Lesson("self-joins", 11, "Self Joins", ["self join", "hierarchies"], ["employees", "customers"], [
            Task("l30-t1", "Show each employee name (as 'employee') with their manager name (as 'manager'). Sort by employee name.", "", "SELECT e.name AS employee, m.name AS manager FROM employees e LEFT JOIN employees m ON m.id = e.manager_id ORDER BY e.name;"),
            Task("l30-t2", "Show each customer name (as 'customer') with their referrer name (as 'referrer'). Sort by customer name.", "", "SELECT c.name AS customer, r.name AS referrer FROM customers c LEFT JOIN customers r ON r.id = c.referrer_id ORDER BY c.name;"),
            Task("l30-t3", "Find pairs of customers from the same country without duplicate mirrored pairs (a.id < b.id). Show customer_a, customer_b, and country. Sort by country.", "", "SELECT a.name AS customer_a, b.name AS customer_b, a.country FROM customers a JOIN customers b ON a.country = b.country AND a.id < b.id ORDER BY a.country;"),
            Task("l30-t4", "Find employees who share a manager (exclude NULL managers, use a.id < b.id). Show employee_a, employee_b, and manager_id. Sort by employee_a.", "", "SELECT a.name AS employee_a, b.name AS employee_b, a.manager_id FROM employees a JOIN employees b ON a.manager_id = b.manager_id AND a.id < b.id WHERE a.manager_id IS NOT NULL ORDER BY employee_a;"),
            Task("l30-t5", "Find customers who placed two distinct orders on the exact same date (a.id < b.id). Show customer_id, ordered_at, order_a_id, and order_b_id. Sort by customer_id then order_a_id.", "", "SELECT a.customer_id, a.ordered_at, a.id AS order_a_id, b.id AS order_b_id FROM orders a JOIN orders b ON a.customer_id = b.customer_id AND a.ordered_at = b.ordered_at AND a.id < b.id ORDER BY a.customer_id, order_a_id;"),
        ]),
    Lesson("semi-anti-joins", 12, "EXISTS and Anti-Joins", ["EXISTS", "NOT EXISTS"], ["customers", "orders", "products", "order_items", "shipments"], [
            Task("l29-t1", "Find customers who have at least one delivered order using EXISTS. Show name, sorted by name.", "", "SELECT name FROM customers WHERE EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id AND orders.status = 'delivered') ORDER BY name;"),
            Task("l29-t2", "Find customers who have never placed an order using NOT EXISTS. Show name, sorted by name.", "", "SELECT name FROM customers WHERE NOT EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id) ORDER BY name;"),
            Task("l29-t3", "Find products that have never been ordered using NOT EXISTS. Show name, sorted by name.", "", "SELECT name FROM products WHERE NOT EXISTS (SELECT 1 FROM order_items WHERE order_items.product_id = products.id) ORDER BY name;"),
            Task("l29-t4", "Find orders that have a shipment row using EXISTS. Show id, sorted by id.", "", "SELECT id FROM orders WHERE EXISTS (SELECT 1 FROM shipments WHERE shipments.order_id = orders.id) ORDER BY id;"),
            Task("l29-t5", "Find delivered orders that do not have a support ticket using NOT EXISTS. Show id, sorted by id.", "", "SELECT id FROM orders WHERE status = 'delivered' AND NOT EXISTS (SELECT 1 FROM support_tickets WHERE support_tickets.order_id = orders.id) ORDER BY id;"),
        ]),
    Lesson("join-patterns", 13, "Join Interview Scenarios", ["identify the join"], ["customers", "orders", "products"], [
        Task("l10j-t1", "Scenario: 'We need a report of all products in our catalog, alongside the quantity sold for each if they were ever ordered.' Return product name and quantity. Sort by product name.", "", "SELECT products.name, order_items.quantity FROM products LEFT JOIN order_items ON order_items.product_id = products.id ORDER BY products.name;"),
        Task("l10j-t2", "Scenario: 'Show me only the customers who actually bought something, and what order IDs they placed.' Return name and order id, sorted by order id.", "", "SELECT customers.name, orders.id FROM customers JOIN orders ON orders.customer_id = customers.id ORDER BY orders.id;"),
        Task("l10j-t3", "Scenario: 'Find instances where two different customers live in the exact same city. Show name_a, name_b, and city (where a.id < b.id).' Sort by city then name_a.", "", "SELECT a.name AS name_a, b.name AS name_b, a.city FROM customers a JOIN customers b ON a.city = b.city AND a.id < b.id ORDER BY a.city, name_a;"),
        Task("l10j-t4", "Scenario: 'Generate a matrix pairing every single customer with every single product.' Return customer name and product name, sorted by customer name then product name.", "", "SELECT customers.name, products.name FROM customers CROSS JOIN products ORDER BY customers.name, products.name;"),
        Task("l10j-t5", "Scenario: 'Identify orphaned data: Find any orders that point to a non-existent customer, OR any customers who have zero orders.' Return order id and customer name, sorted by order id.", "", "SELECT orders.id, customers.name FROM orders FULL JOIN customers ON customers.id = orders.customer_id WHERE orders.id IS NULL OR customers.id IS NULL ORDER BY orders.id;"),
    ]),
    Lesson("joins-capstone", 14, "Joins: Interview Capstone", ["Hint-Free", "Data Modeling"], ["customers", "orders", "order_items", "products", "shipments", "employees", "support_tickets"], [
        Task("jc-t1", "Identify customers who registered but have never placed an order. Return their name.", "", "SELECT customers.name FROM customers LEFT JOIN orders ON orders.customer_id = customers.id WHERE orders.id IS NULL;"),
        Task("jc-t2", "Find products that are currently out of stock (stock = 0) but have been ordered at least once. Return the product name.", "", "SELECT DISTINCT products.name FROM products JOIN order_items ON order_items.product_id = products.id WHERE products.stock = 0;"),
        Task("jc-t3", "List all orders that have no matching shipment tracking info. Return the order id and status.", "", "SELECT orders.id, orders.status FROM orders LEFT JOIN shipments ON shipments.order_id = orders.id WHERE shipments.id IS NULL;"),
        Task("jc-t4", "Show each employee's name alongside their direct manager's name as 'manager'.", "", "SELECT e.name, m.name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id;"),
        Task("jc-t5", "Find all products that have never been ordered. Return the product name.", "", "SELECT products.name FROM products LEFT JOIN order_items ON order_items.product_id = products.id WHERE order_items.id IS NULL;"),
        Task("jc-t6", "Get the names of customers who were referred by another customer, along with the referrer's name as 'referrer'.", "", "SELECT c.name, r.name AS referrer FROM customers c JOIN customers r ON c.referrer_id = r.id;"),
        Task("jc-t7", "Generate a list of all possible combinations of employees and support tickets for a brute-force audit. Return employee name and ticket id.", "", "SELECT employees.name, support_tickets.id FROM employees CROSS JOIN support_tickets;"),
        Task("jc-t8", "Retrieve all shipments that were delivered, along with the customer's name who received it. Return customer name and shipment delivered_at.", "", "SELECT customers.name, shipments.delivered_at FROM shipments JOIN orders ON orders.id = shipments.order_id JOIN customers ON customers.id = orders.customer_id WHERE shipments.delivered_at IS NOT NULL;"),
        Task("jc-t9", "Find the full order details for order ID 101. Return order_id, product name, quantity, and unit_price.", "", "SELECT order_items.order_id, products.name, order_items.quantity, order_items.unit_price FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.order_id = 101;"),
        Task("jc-t10", "Identify customers who placed an order that was subsequently shipped. Return unique customer names.", "", "SELECT DISTINCT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id JOIN shipments ON shipments.order_id = orders.id;"),
        Task("jc-t11", "List any support tickets that are unassigned or assigned to an employee who no longer exists. Return ticket id and issue.", "", "SELECT support_tickets.id, support_tickets.issue FROM support_tickets LEFT JOIN employees ON employees.id = support_tickets.employee_id WHERE employees.id IS NULL;"),
        Task("jc-t12", "Provide a master list of all customers and all orders to highlight data anomalies (e.g. orders without customers). Return customer name and order id.", "", "SELECT customers.name, orders.id FROM customers FULL JOIN orders ON orders.customer_id = customers.id;"),
        Task("jc-t13", "Get the names of employees who actively manage someone else.", "", "SELECT DISTINCT m.name FROM employees e JOIN employees m ON e.manager_id = m.id;"),
        Task("jc-t14", "Find customers whose orders were shipped via 'FedEx'. Return unique customer names.", "", "SELECT DISTINCT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id JOIN shipments ON shipments.order_id = orders.id WHERE shipments.carrier = 'FedEx';"),
        Task("jc-t15", "Show the unique product categories that have been ordered by customers from 'India'.", "", "SELECT DISTINCT products.category FROM products JOIN order_items ON order_items.product_id = products.id JOIN orders ON orders.id = order_items.order_id JOIN customers ON customers.id = orders.customer_id WHERE customers.country = 'India';"),
        Task("jc-t16", "Determine which employees have submitted support tickets under their own account (assuming employee email matches customer email). Return the employee name.", "", "SELECT DISTINCT employees.name FROM employees JOIN customers ON customers.email = employees.email JOIN support_tickets ON support_tickets.customer_id = customers.id;"),
        Task("jc-t17", "List all order IDs that contain the product 'MacBook Pro'.", "", "SELECT DISTINCT order_items.order_id FROM order_items JOIN products ON products.id = order_items.product_id WHERE products.name = 'MacBook Pro';"),
        Task("jc-t18", "Find shipments that were delayed (delivered_at is later than shipped_at) and the associated customer name. Return customer name and shipment id.", "", "SELECT customers.name, shipments.id FROM shipments JOIN orders ON orders.id = shipments.order_id JOIN customers ON customers.id = orders.customer_id WHERE shipments.delivered_at > shipments.shipped_at;"),
        Task("jc-t19", "Show a list of all products alongside any order items they appear in. Include products with no sales. Return product name and order_item id.", "", "SELECT products.name, order_items.id FROM products LEFT JOIN order_items ON order_items.product_id = products.id;"),
        Task("jc-t20", "Identify pairs of customers who reside in the same country. Exclude mirroring pairs (e.g., A-B and B-A). Return c1_name, c2_name, and country.", "", "SELECT c1.name AS c1_name, c2.name AS c2_name, c1.country FROM customers c1 JOIN customers c2 ON c1.country = c2.country AND c1.id < c2.id;"),
    ]),
    Lesson("nulls", 15, "Working with NULL", ["IS NULL", "COALESCE"], ["customers", "employees", "shipments"], [
        Task("l8-t1", "Show customer name and referrer id as 'referrer', replacing NULL referrer_id with 'Direct' using COALESCE. Sort by name.", "", "SELECT name, COALESCE(CAST(referrer_id AS TEXT), 'Direct') AS referrer FROM customers ORDER BY name;"),
        Task("l8-t2", "Find employees who do not have a manager. Show name and team, sorted by name.", "", "SELECT name, team FROM employees WHERE manager_id IS NULL ORDER BY name;"),
        Task("l8-t3", "Show each shipment's order_id and a 'delivery_status' label: 'Delivered' if delivered_at exists, otherwise 'In transit'. Sort by order_id.", "", "SELECT order_id, CASE WHEN delivered_at IS NULL THEN 'In transit' ELSE 'Delivered' END AS delivery_status FROM shipments ORDER BY order_id;"),
        Task("l8-t4", "Show support tickets with no resolved date. Return id, status, and resolved_at, sorted by id.", "", "SELECT id, status, resolved_at FROM support_tickets WHERE resolved_at IS NULL ORDER BY id;"),
        Task("l8-t5", "Show each employee's name and their manager's name as 'manager', using 'No manager' when there is no manager. Sort by employee id.", "", "SELECT e.name, COALESCE(m.name, 'No manager') AS manager FROM employees e LEFT JOIN employees m ON m.id = e.manager_id ORDER BY e.id;"),
    ]),
    Lesson("expressions", 16, "Expressions", ["AS", "CASE", "calculation"], ["order_items", "products", "employees"], [
        Task("l9-t1", "Show each order item's order_id, product_id, and subtotal (quantity × unit_price, as 'subtotal'), sorted by order_id then product_id.", "", "SELECT order_id, product_id, quantity * unit_price AS subtotal FROM order_items ORDER BY order_id, product_id;"),
        Task("l9-t2", "Show each product's name and price increased by 10% as 'projected_price', rounded to 2 decimals. Sort by name.", "", "SELECT name, ROUND(price * 1.10, 2) AS projected_price FROM products ORDER BY name;"),
        Task("l9-t3", "Show product name and a 'stock_status' label: 'Low stock' when stock < 20, otherwise 'Ready'. Sort by name.", "", "SELECT name, CASE WHEN stock < 20 THEN 'Low stock' ELSE 'Ready' END AS stock_status FROM products ORDER BY name;"),
        Task("l9-t4", "Show each employee's name and monthly salary (salary / 12, rounded to 2 decimals, as 'monthly_salary'). Sort by name.", "", "SELECT name, ROUND(salary / 12.0, 2) AS monthly_salary FROM employees ORDER BY name;"),
        Task("l9-t5", "Show each order item's order_id and discounted subtotal (quantity × unit_price × 0.95, rounded to 2 decimals, as 'discounted_subtotal'). Sort by order_id then discounted_subtotal.", "", "SELECT order_id, ROUND(quantity * unit_price * 0.95, 2) AS discounted_subtotal FROM order_items ORDER BY order_id, discounted_subtotal;"),
    ]),
    Lesson("string-functions", 17, "String Functions", ["LOWER", "SUBSTR", "LENGTH"], ["customers", "products"], [
            Task("l21-t1", "Show customer names in lowercase (as 'name_lower') with their city, sorted by name_lower.", "", "SELECT lower(name) AS name_lower, city FROM customers ORDER BY name_lower;"),
            Task("l21-t2", "Show product name and the first four characters of each category (as 'category_prefix'), sorted by name.", "", "SELECT name, substr(category, 1, 4) AS category_prefix FROM products ORDER BY name;"),
            Task("l21-t3", "Find customers whose city name has more than 6 characters. Show name, city, and length(city) as 'city_length', sorted by city_length descending.", "", "SELECT name, city, length(city) AS city_length FROM customers WHERE length(city) > 6 ORDER BY city_length DESC;"),
            Task("l21-t4", "Build a customer label formatted as 'name - country' (as 'customer_label'), sorted by customer_label.", "", "SELECT name || ' - ' || country AS customer_label FROM customers ORDER BY customer_label;"),
            Task("l21-t5", "Find products whose lowercase name contains 'usb' or 'desk'. Show name, sorted by name.", "", "SELECT name FROM products WHERE lower(name) LIKE '%usb%' OR lower(name) LIKE '%desk%' ORDER BY name;"),
        ]),
    Lesson("date-analytics", 18, "Date Analytics", ["strftime", "julianday", "cohorts"], ["customers", "orders", "shipments"], [
            Task("l22-t1", "Count orders by calendar month. Show month (first 7 chars of ordered_at, as 'order_month') and count as 'order_count', sorted by order_month.", "", "SELECT substr(ordered_at, 1, 7) AS order_month, COUNT(*) AS order_count FROM orders GROUP BY order_month ORDER BY order_month;"),
            Task("l22-t2", "Find the number of days between shipment and delivery for delivered shipments. Show order_id and days as 'delivery_days' (integer), sorted by order_id.", "", "SELECT order_id, CAST(julianday(delivered_at) - julianday(shipped_at) AS INTEGER) AS delivery_days FROM shipments WHERE delivered_at IS NOT NULL ORDER BY order_id;"),
            Task("l22-t3", "Show customer name and signup quarter (as 'signup_quarter', formatted like 'Q1'). Sort by signup_date.", "", "SELECT name, 'Q' || ((CAST(strftime('%m', signup_date) AS INTEGER) + 2) / 3) AS signup_quarter FROM customers ORDER BY signup_date;"),
            Task("l22-t4", "Find orders placed in Q1 2024 (Jan-Mar). Show id and ordered_at, sorted by ordered_at.", "", "SELECT id, ordered_at FROM orders WHERE ordered_at >= '2024-01-01' AND ordered_at < '2024-04-01' ORDER BY ordered_at;"),
            Task("l22-t5", "Calculate days from each customer's signup to their first order (as 'days_to_first_order', integer). Join customers and orders, group by customer. Sort by days_to_first_order.", "", "SELECT customers.name, CAST(julianday(MIN(orders.ordered_at)) - julianday(customers.signup_date) AS INTEGER) AS days_to_first_order FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name, customers.signup_date ORDER BY days_to_first_order;"),
        ]),
    Lesson("dates-advanced", 19, "Advanced Dates", ["strftime", "date modifiers"], ["orders", "shipments"], [
        Task("l45-t1", "Extract just the year (YYYY format) from the 'ordered_at' column in orders using strftime(). Show id and 'year', sorted by id.", "", "SELECT id, strftime('%Y', ordered_at) AS year FROM orders ORDER BY id;"),
        Task("l45-t2", "Find orders placed exactly on a Sunday. Use strftime('%w', ordered_at) where '0' is Sunday. Show id, sorted by id.", "", "SELECT id FROM orders WHERE strftime('%w', ordered_at) = '0' ORDER BY id;"),
        Task("l45-t3", "Add 7 days to the 'ordered_at' date using the 'datetime' function with the '+7 days' modifier. Show id and 'projected_delivery', sorted by id.", "", "SELECT id, datetime(ordered_at, '+7 days') AS projected_delivery FROM orders ORDER BY id;"),
        Task("l45-t4", "Show the number of days between 'ordered_at' and 'shipped_at' for delivered shipments. Use julianday() difference. Return order_id and 'days_to_ship' (rounded to 2), sorted by order_id.", "", "SELECT orders.id AS order_id, ROUND(julianday(shipments.shipped_at) - julianday(orders.ordered_at), 2) AS days_to_ship FROM orders JOIN shipments ON shipments.order_id = orders.id WHERE shipments.shipped_at IS NOT NULL ORDER BY orders.id;"),
    ]),
    Lesson("data-types", 20, "Data Types & Casting", ["CAST", "TYPEOF"], ["order_items", "products"], [
        Task("l46-t1", "Cast the 'price' of products from REAL to INTEGER (which truncates the decimal). Show name and 'int_price', sorted by name.", "", "SELECT name, CAST(price AS INTEGER) AS int_price FROM products ORDER BY name;"),
        Task("l46-t2", "Find the dynamic type of the 'status' column in the orders table using TYPEOF(). Return id and 'status_type', sorted by id. (SQLite uses dynamic typing!).", "", "SELECT id, TYPEOF(status) AS status_type FROM orders ORDER BY id;"),
        Task("l46-t3", "In SQL, dividing integers yields an integer. Cast 'stock' to REAL before dividing by 10 to get a float. Return name and 'stock_fraction', sorted by name.", "", "SELECT name, CAST(stock AS REAL) / 10 AS stock_fraction FROM products ORDER BY name;"),
    ]),
    Lesson("data-cleaning", 21, "Data Cleaning Queries", ["TRIM", "COALESCE", "CASE"], ["customers", "products", "shipments"], [
            Task("l33-t1", "Show customer name and tier in uppercase (as 'tier_label'). Sort by name.", "", "SELECT name, upper(tier) AS tier_label FROM customers ORDER BY name;"),
            Task("l33-t2", "Show product name and rating, replacing NULL ratings with 0 (as 'rating_safe'). Sort by name.", "", "SELECT name, COALESCE(rating, 0) AS rating_safe FROM products ORDER BY name;"),
            Task("l33-t3", "Classify products by price: 'budget' if price < 25, 'standard' if price < 75, else 'premium' (as 'price_band'). Show name and price_band, sorted by price then name.", "", "SELECT name, CASE WHEN price < 25 THEN 'budget' WHEN price < 75 THEN 'standard' ELSE 'premium' END AS price_band FROM products ORDER BY price, name;"),
            Task("l33-t4", "Show shipment order_id and delivery date, replacing NULL delivered_at with 'Pending' (as 'delivery_status'). Sort by order_id.", "", "SELECT order_id, COALESCE(delivered_at, 'Pending') AS delivery_status FROM shipments ORDER BY order_id;"),
            Task("l33-t5", "Create a normalized product key by lowercasing the name and replacing spaces with hyphens (as 'product_key'). Show name and product_key, sorted by name.", "", "SELECT name, replace(lower(name), ' ', '-') AS product_key FROM products ORDER BY name;"),
        ]),
    Lesson("expressions-capstone", 22, "Expressions & Types: Interview Capstone", ["Hint-Free", "Data Cleaning"], ["customers", "orders", "products"], [
        Task("ec-t1", "Extract the domain name from every customer's email address. Return email and 'domain'.", "", "SELECT email, SUBSTR(email, INSTR(email, '@') + 1) AS domain FROM customers;"),
        Task("ec-t2", "Calculate the total value of inventory for each product if all items were sold at full price. Return name and 'total_value'.", "", "SELECT name, price * stock AS total_value FROM products;"),
        Task("ec-t3", "Format the customer names to be completely uppercase.", "", "SELECT UPPER(name) FROM customers;"),
        Task("ec-t4", "Determine the length (number of characters) of each product's name. Return name and 'name_length'.", "", "SELECT name, LENGTH(name) AS name_length FROM products;"),
        Task("ec-t5", "Categorize products by price: '< 50' as 'Cheap', '50 - 500' as 'Mid', '> 500' as 'Premium'. Return name and 'price_tier'.", "", "SELECT name, CASE WHEN price < 50 THEN 'Cheap' WHEN price <= 500 THEN 'Mid' ELSE 'Premium' END AS price_tier FROM products;"),
        Task("ec-t6", "Replace the word 'Pro' with 'Professional' in any product name that contains it. Return original name and 'new_name'.", "", "SELECT name, REPLACE(name, 'Pro', 'Professional') AS new_name FROM products WHERE name LIKE '%Pro%';"),
        Task("ec-t7", "Extract just the year from the 'ordered_at' column for all orders. Return order id and 'order_year'.", "", "SELECT id, strftime('%Y', ordered_at) AS order_year FROM orders;"),
        Task("ec-t8", "Identify orders placed in February of any year. Return order id and ordered_at.", "", "SELECT id, ordered_at FROM orders WHERE strftime('%m', ordered_at) = '02';"),
        Task("ec-t9", "Return customer names, providing a fallback string 'No Referrer' if their referrer_id is null.", "", "SELECT name, COALESCE(CAST(referrer_id AS TEXT), 'No Referrer') FROM customers;"),
        Task("ec-t10", "Calculate a 15% discount for all 'Electronics' products. Return name and 'discounted_price' rounded to 2 decimals.", "", "SELECT name, ROUND(price * 0.85, 2) AS discounted_price FROM products WHERE category = 'Electronics';"),
        Task("ec-t11", "Find the day of the week (0-6) each order was placed. Return order id and 'day_of_week'.", "", "SELECT id, strftime('%w', ordered_at) AS day_of_week FROM orders;"),
        Task("ec-t12", "Combine customer name and country into a single string formatted like 'Name (Country)'. Return 'customer_info'.", "", "SELECT name || ' (' || country || ')' AS customer_info FROM customers;"),
        Task("ec-t13", "Identify the exact dynamic type of the 'price' column in the products table. Return name and 'price_type'.", "", "SELECT name, typeof(price) AS price_type FROM products;"),
        Task("ec-t14", "Force the 'stock' column (INTEGER) to be treated as a REAL number and divide by 3. Return name and 'third_stock'.", "", "SELECT name, CAST(stock AS REAL) / 3 AS third_stock FROM products;"),
        Task("ec-t15", "Extract the month and year together (e.g. '2024-01') from orders. Return order id and 'month_year'.", "", "SELECT id, substr(ordered_at, 1, 7) AS month_year FROM orders;"),
        Task("ec-t16", "Calculate how many days old an order is, assuming 'today' is '2024-02-01'. Return order id and 'days_old' rounded to 1 decimal.", "", "SELECT id, ROUND(julianday('2024-02-01') - julianday(ordered_at), 1) AS days_old FROM orders;"),
        Task("ec-t17", "Identify if a product's stock is an even or odd number using modulo. Return name and 'parity' ('Even' or 'Odd').", "", "SELECT name, CASE WHEN stock % 2 = 0 THEN 'Even' ELSE 'Odd' END AS parity FROM products;"),
        Task("ec-t18", "Trim any potential leading or trailing spaces from customer names (simulate cleaning dirty data). Return 'clean_name'.", "", "SELECT TRIM(name) AS clean_name FROM customers;"),
        Task("ec-t19", "Calculate the absolute difference between the product price and 100. Return name and 'diff_100'.", "", "SELECT name, ABS(price - 100) AS diff_100 FROM products;"),
        Task("ec-t20", "Use NULLIF to return NULL if the product stock is 0, otherwise return the stock. Return name and 'safe_stock'.", "", "SELECT name, NULLIF(stock, 0) AS safe_stock FROM products;"),
    ]),
    Lesson("aggregates", 23, "Aggregates", ["COUNT", "SUM", "AVG"], ["products", "orders", "order_items"], [
        Task("l10-t1", "Count all products. Alias the result as 'product_count'.", "", "SELECT COUNT(*) AS product_count FROM products;"),
        Task("l10-t2", "Find the average product price, rounded to 2 decimals. Alias as 'average_price'.", "", "SELECT ROUND(AVG(price), 2) AS average_price FROM products;"),
        Task("l10-t3", "Find the total revenue from all order items (sum of quantity × unit_price), rounded to 2 decimals. Alias as 'revenue'.", "", "SELECT ROUND(SUM(quantity * unit_price), 2) AS revenue FROM order_items;"),
        Task("l10-t4", "Find the lowest and highest product price. Alias as 'lowest_price' and 'highest_price'.", "", "SELECT MIN(price) AS lowest_price, MAX(price) AS highest_price FROM products;"),
        Task("l10-t5", "Count orders grouped by status. Show status and count as 'order_count', sorted by status.", "", "SELECT status, COUNT(*) AS order_count FROM orders GROUP BY status ORDER BY status;"),
    ]),
    Lesson("grouping", 24, "GROUP BY and HAVING", ["GROUP BY", "HAVING"], ["products", "orders", "order_items", "customers"], [
        Task("l11-t1", "Count products in each category. Show category and count as 'product_count', sorted by category.", "", "SELECT category, COUNT(*) AS product_count FROM products GROUP BY category ORDER BY category;"),
        Task("l11-t2", "Find total revenue per order (sum of quantity × unit_price, rounded to 2 decimals). Show order_id and total as 'order_total', sorted by order_id.", "", "SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS order_total FROM order_items GROUP BY order_id ORDER BY order_id;"),
        Task("l11-t3", "Find customers with more than one order. Join customers with orders. Show customer name and count as 'order_count', sorted by name.", "", "SELECT customers.name, COUNT(orders.id) AS order_count FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name HAVING COUNT(orders.id) > 1 ORDER BY customers.name;"),
        Task("l11-t4", "Find product categories whose average price exceeds 50. Show category and average as 'average_price' (rounded to 2 decimals), sorted by category.", "", "SELECT category, ROUND(AVG(price), 2) AS average_price FROM products GROUP BY category HAVING AVG(price) > 50 ORDER BY category;"),
        Task("l11-t5", "Find total quantity sold for each product. Join products with order_items. Show product name and sum as 'units_sold', sorted by units_sold descending then name.", "", "SELECT products.name, SUM(order_items.quantity) AS units_sold FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name ORDER BY units_sold DESC, products.name;"),
    ]),
    Lesson("conditional-aggregation", 25, "Conditional Aggregation", ["SUM(CASE)", "COUNT(CASE)"], ["orders", "order_items", "customers", "products"], [
            Task("l23-t1", "For each order channel, count delivered orders (as 'delivered_orders') and non-delivered orders (as 'other_orders') using SUM(CASE...). Sort by channel.", "", "SELECT channel, SUM(CASE WHEN status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders, SUM(CASE WHEN status <> 'delivered' THEN 1 ELSE 0 END) AS other_orders FROM orders GROUP BY channel ORDER BY channel;"),
            Task("l23-t2", "For each customer tier, count customers from India (as 'india_customers') and outside India (as 'other_customers') using SUM(CASE...). Sort by tier.", "", "SELECT tier, SUM(CASE WHEN country = 'India' THEN 1 ELSE 0 END) AS india_customers, SUM(CASE WHEN country <> 'India' THEN 1 ELSE 0 END) AS other_customers FROM customers GROUP BY tier ORDER BY tier;"),
            Task("l23-t3", "For each product category, count products with stock below 20 (as 'low_stock') and stock 20 or above (as 'healthy_stock') using SUM(CASE...). Sort by category.", "", "SELECT category, SUM(CASE WHEN stock < 20 THEN 1 ELSE 0 END) AS low_stock, SUM(CASE WHEN stock >= 20 THEN 1 ELSE 0 END) AS healthy_stock FROM products GROUP BY category ORDER BY category;"),
            Task("l23-t4", "For each customer, calculate delivered revenue (as 'delivered_revenue') and cancelled revenue (as 'cancelled_revenue') separately, rounded to 2 decimals. Join customers, orders, and order_items. Sort by customer name.", "", "SELECT customers.name, ROUND(SUM(CASE WHEN orders.status = 'delivered' THEN order_items.quantity * order_items.unit_price ELSE 0 END), 2) AS delivered_revenue, ROUND(SUM(CASE WHEN orders.status = 'cancelled' THEN order_items.quantity * order_items.unit_price ELSE 0 END), 2) AS cancelled_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name ORDER BY customers.name;"),
            Task("l23-t5", "Show total units sold split into Electronics units (as 'electronics_units') and all other units (as 'non_electronics_units') using SUM(CASE...). Join products and order_items.", "", "SELECT SUM(CASE WHEN products.category = 'Electronics' THEN order_items.quantity ELSE 0 END) AS electronics_units, SUM(CASE WHEN products.category <> 'Electronics' THEN order_items.quantity ELSE 0 END) AS non_electronics_units FROM products JOIN order_items ON order_items.product_id = products.id;"),
        ]),
    Lesson("aggregations-capstone", 26, "Aggregations: Interview Capstone", ["Hint-Free", "Data Analytics"], ["customers", "orders", "order_items", "products", "shipments", "employees", "support_tickets"], [
        Task("ac-t1", "Find the total revenue generated by each customer. Return customer name and 'revenue'.", "", "SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name;"),
        Task("ac-t2", "Calculate the average price of products in each category. Return category and 'avg_price'.", "", "SELECT category, AVG(price) AS avg_price FROM products GROUP BY category;"),
        Task("ac-t3", "Count the number of support tickets assigned to each employee. Return employee name and 'ticket_count'. Include employees with zero tickets.", "", "SELECT employees.name, COUNT(support_tickets.id) AS ticket_count FROM employees LEFT JOIN support_tickets ON support_tickets.employee_id = employees.id GROUP BY employees.id, employees.name;"),
        Task("ac-t4", "Determine which product categories have strictly less than 50 items in total stock. Return category and 'total_stock'.", "", "SELECT category, SUM(stock) AS total_stock FROM products GROUP BY category HAVING SUM(stock) < 50;"),
        Task("ac-t5", "Find the maximum quantity ever ordered in a single line item for each product. Return product name and 'max_qty'.", "", "SELECT products.name, MAX(order_items.quantity) AS max_qty FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name;"),
        Task("ac-t6", "Calculate the total number of orders placed in each country. Return country and 'order_count'.", "", "SELECT customers.country, COUNT(orders.id) AS order_count FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.country;"),
        Task("ac-t7", "Identify customers who have placed exactly 1 order. Return customer name.", "", "SELECT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name HAVING COUNT(orders.id) = 1;"),
        Task("ac-t8", "Find the earliest and latest order date for each customer. Return customer name, 'first_order', and 'last_order'.", "", "SELECT customers.name, MIN(orders.ordered_at) AS first_order, MAX(orders.ordered_at) AS last_order FROM customers JOIN orders ON orders.customer_id = customers.id GROUP BY customers.id, customers.name;"),
        Task("ac-t9", "Calculate the total inventory value (price * stock) per category. Return category and 'inventory_value'.", "", "SELECT category, SUM(price * stock) AS inventory_value FROM products GROUP BY category;"),
        Task("ac-t10", "Count how many orders each shipping carrier has handled. Return carrier and 'handled_count'.", "", "SELECT carrier, COUNT(id) AS handled_count FROM shipments GROUP BY carrier;"),
        Task("ac-t11", "Determine the average time to ship (shipped_at - ordered_at in days) for FedEx shipments. Use julianday(). Return carrier and 'avg_days'.", "", "SELECT shipments.carrier, AVG(julianday(shipments.shipped_at) - julianday(orders.ordered_at)) AS avg_days FROM shipments JOIN orders ON orders.id = shipments.order_id WHERE shipments.carrier = 'FedEx' GROUP BY shipments.carrier;"),
        Task("ac-t12", "Find the total number of distinct products ordered by each customer. Return customer name and 'unique_products'.", "", "SELECT customers.name, COUNT(DISTINCT order_items.product_id) AS unique_products FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name;"),
        Task("ac-t13", "Identify employees who manage more than 1 person. Return manager name and 'report_count'.", "", "SELECT m.name, COUNT(e.id) AS report_count FROM employees m JOIN employees e ON e.manager_id = m.id GROUP BY m.id, m.name HAVING COUNT(e.id) > 1;"),
        Task("ac-t14", "Calculate the total revenue lost to discounted items (unit_price < price) per product. Return product name and 'lost_revenue'.", "", "SELECT products.name, SUM((products.price - order_items.unit_price) * order_items.quantity) AS lost_revenue FROM products JOIN order_items ON order_items.product_id = products.id WHERE order_items.unit_price < products.price GROUP BY products.id, products.name;"),
        Task("ac-t15", "Find the month (YYYY-MM format) with the highest number of orders. Return 'month' and 'order_count', ordered by order_count DESC limit 1.", "", "SELECT substr(ordered_at, 1, 7) AS month, COUNT(id) AS order_count FROM orders GROUP BY substr(ordered_at, 1, 7) ORDER BY order_count DESC LIMIT 1;"),
        Task("ac-t16", "Determine the average stock level across all products in the database. Return 'avg_stock'.", "", "SELECT AVG(stock) AS avg_stock FROM products;"),
        Task("ac-t17", "Identify product categories where the average price exceeds 500. Return category.", "", "SELECT category FROM products GROUP BY category HAVING AVG(price) > 500;"),
        Task("ac-t18", "Count the number of unresolved (status != 'resolved') tickets per employee. Return employee name and 'unresolved_count'.", "", "SELECT employees.name, COUNT(support_tickets.id) AS unresolved_count FROM employees JOIN support_tickets ON support_tickets.employee_id = employees.id WHERE support_tickets.status != 'resolved' GROUP BY employees.id, employees.name;"),
        Task("ac-t19", "Calculate the percentage of shipments that are 'FedEx' vs other carriers. Return 'fedex_percentage' rounded to 2 decimals.", "", "SELECT ROUND(SUM(CASE WHEN carrier = 'FedEx' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS fedex_percentage FROM shipments;"),
        Task("ac-t20", "Find customers whose total lifetime spend exceeds 1000. Return customer name.", "", "SELECT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name HAVING SUM(order_items.quantity * order_items.unit_price) > 1000;"),
    ]),
    Lesson("union-intersect-except", 27, "UNION / INTERSECT / EXCEPT", ["UNION", "UNION ALL", "INTERSECT", "EXCEPT"], ["customers", "orders", "products", "order_items", "shipments"], [
        Task("l19u-t1", "List every distinct country that appears in the customers table combined with the single value 'Canada'. Show country, sorted alphabetically. Use UNION.", "", "SELECT country FROM customers UNION SELECT 'Canada' AS country ORDER BY country;"),
        Task("l19u-t2", "Show all customer cities AND all shipment carriers in a single column named 'label'. Include duplicates. Sort by label. Use UNION ALL.", "", "SELECT city AS label FROM customers UNION ALL SELECT carrier AS label FROM shipments ORDER BY label;"),
        Task("l19u-t3", "Find countries that have BOTH gold-tier AND silver-tier customers. Show country, sorted by country. Use INTERSECT.", "", "SELECT country FROM customers WHERE tier = 'gold' INTERSECT SELECT country FROM customers WHERE tier = 'silver' ORDER BY country;"),
        Task("l19u-t4", "Find product ids that exist in the products table but have never appeared in order_items. Show id, sorted by id. Use EXCEPT.", "", "SELECT id FROM products EXCEPT SELECT product_id FROM order_items ORDER BY id;"),
        Task("l19u-t5", "Find customer ids who placed orders via 'web' AND via 'mobile' (both channels). Show customer_id, sorted. Use INTERSECT.", "", "SELECT customer_id FROM orders WHERE channel = 'web' INTERSECT SELECT customer_id FROM orders WHERE channel = 'mobile' ORDER BY customer_id;"),
        Task("l19u-t6", "Build a unified order status report: for each status show 'delivered', 'cancelled', or 'other' orders count. Use UNION ALL to combine three separate SELECT statements (one per status group), each returning status_group and order_count. Sort by status_group.", "", "SELECT 'delivered' AS status_group, COUNT(*) AS order_count FROM orders WHERE status = 'delivered' UNION ALL SELECT 'cancelled' AS status_group, COUNT(*) AS order_count FROM orders WHERE status = 'cancelled' UNION ALL SELECT 'other' AS status_group, COUNT(*) AS order_count FROM orders WHERE status NOT IN ('delivered', 'cancelled') ORDER BY status_group;"),
    ]),
    Lesson("set-operations-advanced", 28, "Set Operations", ["UNION", "INTERSECT", "EXCEPT"], ["customers", "orders", "products", "order_items"], [
            Task("l31-t1", "List countries that have both gold and silver customers using INTERSECT. Show country, sorted by country.", "", "SELECT country FROM customers WHERE tier = 'gold' INTERSECT SELECT country FROM customers WHERE tier = 'silver' ORDER BY country;"),
            Task("l31-t2", "List product ids that exist in products but not in order_items using EXCEPT. Show id, sorted by id.", "", "SELECT id FROM products EXCEPT SELECT product_id FROM order_items ORDER BY id;"),
            Task("l31-t3", "Combine customer cities and shipment carriers into a single column 'label' using UNION. Sort by label.", "", "SELECT city AS label FROM customers UNION SELECT carrier AS label FROM shipments ORDER BY label;"),
            Task("l31-t4", "Find customer_ids who ordered via both web and mobile using INTERSECT. Show customer_id, sorted by customer_id.", "", "SELECT customer_id FROM orders WHERE channel = 'web' INTERSECT SELECT customer_id FROM orders WHERE channel = 'mobile' ORDER BY customer_id;"),
            Task("l31-t5", "Find ordered product_ids that are not active stocked products (discontinued = 0 and stock > 0) using EXCEPT. Show product_id, sorted by product_id.", "", "SELECT product_id FROM order_items EXCEPT SELECT id FROM products WHERE discontinued = 0 AND stock > 0 ORDER BY product_id;"),
        ]),
    Lesson("advanced-review", 29, "Subqueries and Sets", ["subquery", "UNION", "EXCEPT"], ["products", "customers", "orders", "order_items"], [
        Task("l19-t1", "Find products priced above the overall average price. Show name and price, sorted by price descending then name.", "", "SELECT name, price FROM products WHERE price > (SELECT AVG(price) FROM products) ORDER BY price DESC, name;"),
        Task("l19-t2", "Find customers who have placed at least one delivered order. Show name, sorted by name. Use a subquery with IN.", "", "SELECT name FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE status = 'delivered') ORDER BY name;"),
        Task("l19-t3", "List all unique countries from customers combined with the literal value 'Canada' using UNION. Sort by country.", "", "SELECT country FROM customers UNION SELECT 'Canada' AS country ORDER BY country;"),
        Task("l19-t4", "Find products that have never appeared in order_items using EXCEPT. Show id and name, sorted by id.", "", "SELECT id, name FROM products EXCEPT SELECT products.id, products.name FROM products JOIN order_items ON order_items.product_id = products.id ORDER BY id;"),
        Task("l19-t5", "Find customers whose total non-cancelled spend exceeds the average order total. Show name and spend (rounded to 2 decimals, as 'spend'), sorted by spend descending.", "", "SELECT customer_totals.name, ROUND(customer_totals.spend, 2) AS spend FROM (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name) AS customer_totals WHERE customer_totals.spend > (SELECT AVG(order_total) FROM (SELECT SUM(quantity * unit_price) AS order_total FROM order_items GROUP BY order_id)) ORDER BY spend DESC;"),
    ]),
    Lesson("sets-capstone", 30, "Sets & Subqueries: Interview Capstone", ["Hint-Free", "Logic"], ["customers", "orders", "products"], [
        Task("sc-t1", "Identify customers who have placed an order. Do not use JOINs. Use a subquery.", "", "SELECT name FROM customers WHERE id IN (SELECT customer_id FROM orders);"),
        Task("sc-t2", "Identify products that have never been ordered. Use a subquery.", "", "SELECT name FROM products WHERE id NOT IN (SELECT product_id FROM order_items);"),
        Task("sc-t3", "Create a single list containing all unique customer names AND all unique product names.", "", "SELECT name FROM customers UNION SELECT name FROM products;"),
        Task("sc-t4", "Create a list of countries where we have customers, but explicitly exclude 'USA'. Do not use WHERE country != 'USA'. Use EXCEPT.", "", "SELECT country FROM customers EXCEPT SELECT 'USA';"),
        Task("sc-t5", "Find products whose price is greater than the average price of all products.", "", "SELECT name, price FROM products WHERE price > (SELECT AVG(price) FROM products);"),
        Task("sc-t6", "List customers who have at least one 'delivered' shipment. Use EXISTS.", "", "SELECT name FROM customers WHERE EXISTS (SELECT 1 FROM orders JOIN shipments ON shipments.order_id = orders.id WHERE orders.customer_id = customers.id AND shipments.delivered_at IS NOT NULL);"),
        Task("sc-t7", "Identify the single most expensive product using a subquery instead of LIMIT.", "", "SELECT name, price FROM products WHERE price = (SELECT MAX(price) FROM products);"),
        Task("sc-t8", "Create a single column containing the IDs of all customers, followed immediately by the IDs of all orders. Preserve duplicates.", "", "SELECT id FROM customers UNION ALL SELECT id FROM orders;"),
        Task("sc-t9", "Find customers who reside in the same country as the customer named 'Alice'. Exclude Alice herself.", "", "SELECT name FROM customers WHERE country = (SELECT country FROM customers WHERE name = 'Alice') AND name != 'Alice';"),
        Task("sc-t10", "List orders placed by customers who were referred by someone (referrer_id is not null). Use a subquery.", "", "SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE referrer_id IS NOT NULL);"),
        Task("sc-t11", "Find product categories that contain a product priced over 1000. Use a subquery.", "", "SELECT DISTINCT category FROM products WHERE category IN (SELECT category FROM products WHERE price > 1000);"),
        Task("sc-t12", "List the email addresses of employees that perfectly match the email addresses of customers. Use INTERSECT.", "", "SELECT email FROM employees INTERSECT SELECT email FROM customers;"),
        Task("sc-t13", "Find the customer who placed the most recent order. Use a subquery for the max date.", "", "SELECT name FROM customers WHERE id = (SELECT customer_id FROM orders WHERE ordered_at = (SELECT MAX(ordered_at) FROM orders));"),
        Task("sc-t14", "Identify orders containing any product from the 'Electronics' category. Use an IN subquery.", "", "SELECT DISTINCT order_id FROM order_items WHERE product_id IN (SELECT id FROM products WHERE category = 'Electronics');"),
        Task("sc-t15", "Find the total number of orders placed by customers from 'India'. Use a scalar subquery in the SELECT clause.", "", "SELECT (SELECT COUNT(*) FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE country = 'India')) AS indian_orders;"),
        Task("sc-t16", "Identify products that are completely out of stock. Use NOT EXISTS.", "", "SELECT name FROM products p WHERE NOT EXISTS (SELECT 1 FROM products WHERE p.id = id AND stock > 0);"),
        Task("sc-t17", "Find all support tickets assigned to employees who also happen to be managers. Use an IN subquery.", "", "SELECT id FROM support_tickets WHERE employee_id IN (SELECT manager_id FROM employees WHERE manager_id IS NOT NULL);"),
        Task("sc-t18", "List the countries that both customers AND employees reside in. (Assume employees have a country field? No, employees don't have country. Skip this, just union all emails from customers and employees).", "", "SELECT email FROM customers UNION ALL SELECT email FROM employees;"),
        Task("sc-t19", "Find orders where the total quantity of items is exactly 1. Use an IN subquery checking order_items.", "", "SELECT id FROM orders WHERE id IN (SELECT order_id FROM order_items GROUP BY order_id HAVING SUM(quantity) = 1);"),
        Task("sc-t20", "Use a correlated subquery to find products whose price is higher than the average price of products IN THEIR OWN CATEGORY.", "", "SELECT p1.name, p1.price FROM products p1 WHERE p1.price > (SELECT AVG(p2.price) FROM products p2 WHERE p1.category = p2.category);"),
    ]),
    Lesson("ctes", 31, "Common Table Expressions", ["WITH", "readability"], ["customers", "orders", "order_items", "products"], [
            Task("l27-t1", "Use a CTE named 'order_totals' to calculate each order's total, then return totals above 100. Show order_id and total (rounded to 2 decimals), sorted by total descending.", "", "WITH order_totals AS (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) SELECT order_id, ROUND(total, 2) AS total FROM order_totals WHERE total > 100 ORDER BY total DESC;"),
            Task("l27-t2", "Use two CTEs: 'customer_spend' (non-cancelled spend per customer) and 'avg_spend' (average of customer_spend). Return customers whose spend exceeds avg_spend. Show name and spend (rounded to 2 decimals), sorted by spend descending.", "", "WITH customer_spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name), avg_spend AS (SELECT AVG(spend) AS avg_spend FROM customer_spend) SELECT name, ROUND(spend, 2) AS spend FROM customer_spend, avg_spend WHERE spend > avg_spend ORDER BY spend DESC;"),
            Task("l27-t3", "Use a CTE named 'product_revenue' to find each product's revenue by category. Then sum by category. Show category and total as 'category_revenue' (rounded to 2 decimals), sorted by category_revenue descending.", "", "WITH product_revenue AS (SELECT products.category, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.category, products.name) SELECT category, ROUND(SUM(revenue), 2) AS category_revenue FROM product_revenue GROUP BY category ORDER BY category_revenue DESC;"),
            Task("l27-t4", "Use a CTE named 'delivered_orders' to filter delivered orders, then list distinct customer names, sorted by name.", "", "WITH delivered_orders AS (SELECT * FROM orders WHERE status = 'delivered') SELECT DISTINCT customers.name FROM delivered_orders JOIN customers ON customers.id = delivered_orders.customer_id ORDER BY customers.name;"),
            Task("l27-t5", "Use a CTE named 'category_counts' to count products per category, then keep categories with at least 2 products. Show category and product_count, sorted by category.", "", "WITH category_counts AS (SELECT category, COUNT(*) AS product_count FROM products GROUP BY category) SELECT category, product_count FROM category_counts WHERE product_count >= 2 ORDER BY category;"),
        ]),
    Lesson("recursive-ctes", 32, "Recursive CTEs", ["WITH RECURSIVE", "hierarchies"], ["employees", "customers"], [
            Task("l28-t1", "List the employee hierarchy starting from the top-level employee (no manager), including depth (0 for top). Show name and depth, sorted by depth then name.", "", "WITH RECURSIVE org(id, name, manager_id, depth) AS (SELECT id, name, manager_id, 0 FROM employees WHERE manager_id IS NULL UNION ALL SELECT employees.id, employees.name, employees.manager_id, org.depth + 1 FROM employees JOIN org ON employees.manager_id = org.id) SELECT name, depth FROM org ORDER BY depth, name;"),
            Task("l28-t2", "Find all employees under manager 'Owen Brooks' (exclude Owen himself). Show name, sorted by name.", "", "WITH RECURSIVE reports(id, name, manager_id) AS (SELECT id, name, manager_id FROM employees WHERE name = 'Owen Brooks' UNION ALL SELECT employees.id, employees.name, employees.manager_id FROM employees JOIN reports ON employees.manager_id = reports.id) SELECT name FROM reports WHERE name <> 'Owen Brooks' ORDER BY name;"),
            Task("l28-t3", "Build a management path for every employee (e.g., 'Rina Kapoor > Owen Brooks > Mei Lin'). Show name and path, sorted by path.", "", "WITH RECURSIVE org(id, name, manager_id, path) AS (SELECT id, name, manager_id, name FROM employees WHERE manager_id IS NULL UNION ALL SELECT employees.id, employees.name, employees.manager_id, org.path || ' > ' || employees.name FROM employees JOIN org ON employees.manager_id = org.id) SELECT name, path FROM org ORDER BY path;"),
            Task("l28-t4", "Walk customer referrals starting from 'Asha Rao' and show referral depth (0 for Asha). Show name and depth, sorted by depth.", "", "WITH RECURSIVE referrals(id, name, depth) AS (SELECT id, name, 0 FROM customers WHERE name = 'Asha Rao' UNION ALL SELECT customers.id, customers.name, referrals.depth + 1 FROM customers JOIN referrals ON customers.referrer_id = referrals.id) SELECT name, depth FROM referrals ORDER BY depth;"),
            Task("l28-t5", "Generate numbers 1 through 5 using a recursive CTE with column 'n'. Sort by n.", "", "WITH RECURSIVE numbers(n) AS (SELECT 1 UNION ALL SELECT n + 1 FROM numbers WHERE n < 5) SELECT n FROM numbers ORDER BY n;"),
        ]),
    Lesson("window-ranking", 33, "Window Ranking", ["ROW_NUMBER", "RANK", "PARTITION BY"], ["products", "customers", "orders", "order_items"], [
            Task("l24-t1", "Rank products by price from highest to lowest. Show name, price, and RANK() as 'price_rank', sorted by price_rank then name.", "", "SELECT name, price, RANK() OVER (ORDER BY price DESC) AS price_rank FROM products ORDER BY price_rank, name;"),
            Task("l24-t2", "Assign row numbers to products within each category, ordered by price descending then name. Show category, name, price, and ROW_NUMBER() as 'category_row'. Sort by category then category_row.", "", "SELECT category, name, price, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, name) AS category_row FROM products ORDER BY category, category_row;"),
            Task("l24-t3", "Rank customers by their non-cancelled spend. Show name, spend (rounded to 2 decimals), and RANK() as 'spend_rank'. Use a subquery to calculate spend first. Sort by spend_rank then name.", "", "SELECT name, ROUND(spend, 2) AS spend, RANK() OVER (ORDER BY spend DESC) AS spend_rank FROM (SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name) AS customer_spend ORDER BY spend_rank, name;"),
            Task("l24-t4", "For every order, number that customer's orders by date. Show customer_id, order id (as 'order_id'), ordered_at, and ROW_NUMBER() as 'customer_order_number'. Sort by customer_id then customer_order_number.", "", "SELECT customer_id, id AS order_id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS customer_order_number FROM orders ORDER BY customer_id, customer_order_number;"),
            Task("l24-t5", "Dense-rank product categories by average product price. Show category, average price (rounded to 2 decimals, as 'average_price'), and DENSE_RANK() as 'category_rank'. Sort by category_rank then category.", "", "SELECT category, ROUND(AVG(price), 2) AS average_price, DENSE_RANK() OVER (ORDER BY AVG(price) DESC) AS category_rank FROM products GROUP BY category ORDER BY category_rank, category;"),
        ]),
    Lesson("window-analytics", 34, "Running Totals and Moving Averages", ["SUM OVER", "AVG OVER"], ["orders", "order_items", "products"], [
            Task("l25-t1", "Show each order's total (as 'order_total') and running revenue (as 'running_revenue') by order date. Group by order, sort by ordered_at then id. Both values rounded to 2 decimals.", "", "SELECT orders.id, orders.ordered_at, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total, ROUND(SUM(SUM(order_items.quantity * order_items.unit_price)) OVER (ORDER BY orders.ordered_at, orders.id), 2) AS running_revenue FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY orders.id, orders.ordered_at ORDER BY orders.ordered_at, orders.id;"),
            Task("l25-t2", "Show each order's total (as 'order_total') and its percentage of all revenue (as 'pct_of_revenue'), both rounded to 2 decimals. Sort by order_id.", "", "SELECT order_id, ROUND(SUM(quantity * unit_price), 2) AS order_total, ROUND(100.0 * SUM(quantity * unit_price) / SUM(SUM(quantity * unit_price)) OVER (), 2) AS pct_of_revenue FROM order_items GROUP BY order_id ORDER BY order_id;"),
            Task("l25-t3", "Show each product's name, category, price, and the category average price (as 'category_avg_price', rounded to 2 decimals) using AVG OVER. Sort by category then name.", "", "SELECT name, category, price, ROUND(AVG(price) OVER (PARTITION BY category), 2) AS category_avg_price FROM products ORDER BY category, name;"),
            Task("l25-t4", "Show each order with the previous order date for the same customer using LAG. Show customer_id, order id (as 'order_id'), ordered_at, and previous_order_at. Sort by customer_id then ordered_at.", "", "SELECT customer_id, id AS order_id, ordered_at, LAG(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS previous_order_at FROM orders ORDER BY customer_id, ordered_at;"),
            Task("l25-t5", "Show each order with the next order date for the same customer using LEAD. Show customer_id, order id (as 'order_id'), ordered_at, and next_order_at. Sort by customer_id then ordered_at.", "", "SELECT customer_id, id AS order_id, ordered_at, LEAD(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS next_order_at FROM orders ORDER BY customer_id, ordered_at;"),
        ]),
    Lesson("top-n-per-group", 35, "Top N Per Group", ["ROW_NUMBER", "filter ranked rows"], ["products", "orders", "order_items"], [
            Task("l26-t1", "Find the most expensive product in each category. Use ROW_NUMBER in a subquery. Show category, name, and price, sorted by category.", "", "SELECT category, name, price FROM (SELECT category, name, price, ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC, name) AS rn FROM products) AS ranked WHERE rn = 1 ORDER BY category;"),
            Task("l26-t2", "Find the top two products by total units sold. Use ROW_NUMBER in a subquery. Show name and units_sold, sorted by units_sold descending then name.", "", "SELECT name, units_sold FROM (SELECT products.name, SUM(order_items.quantity) AS units_sold, ROW_NUMBER() OVER (ORDER BY SUM(order_items.quantity) DESC, products.name) AS rn FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name) AS ranked WHERE rn <= 2 ORDER BY units_sold DESC, name;"),
            Task("l26-t3", "Find each customer's latest order. Use ROW_NUMBER in a subquery. Show customer_id, order id (as 'order_id'), and ordered_at, sorted by customer_id.", "", "SELECT customer_id, id AS order_id, ordered_at FROM (SELECT customer_id, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at DESC, id DESC) AS rn FROM orders) AS ranked WHERE rn = 1 ORDER BY customer_id;"),
            Task("l26-t4", "Find the top product by revenue within each category. Use ROW_NUMBER in a subquery. Show category, name, and revenue (rounded to 2 decimals), sorted by category.", "", "SELECT category, name, ROUND(revenue, 2) AS revenue FROM (SELECT products.category, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue, ROW_NUMBER() OVER (PARTITION BY products.category ORDER BY SUM(order_items.quantity * order_items.unit_price) DESC, products.name) AS rn FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.category, products.name) AS ranked WHERE rn = 1 ORDER BY category;"),
            Task("l26-t5", "Find the two newest orders per channel. Use ROW_NUMBER in a subquery. Show channel, order id (as 'order_id'), and ordered_at, sorted by channel then ordered_at descending.", "", "SELECT channel, id AS order_id, ordered_at FROM (SELECT channel, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY channel ORDER BY ordered_at DESC, id DESC) AS rn FROM orders) AS ranked WHERE rn <= 2 ORDER BY channel, ordered_at DESC;"),
        ]),
    Lesson("advanced-capstone", 36, "Advanced Queries: Interview Capstone", ["Hint-Free", "CTEs", "Windows"], ["customers", "orders", "products"], [
        Task("adc-t1", "Rank all products by price from highest to lowest. Give equal prices the same rank and skip ranks (e.g. 1, 2, 2, 4). Return name, price, and rank.", "", "SELECT name, price, RANK() OVER(ORDER BY price DESC) AS rnk FROM products;"),
        Task("adc-t2", "Rank all products by price from highest to lowest. Give equal prices the same rank but do NOT skip ranks (e.g. 1, 2, 2, 3). Return name, price, and rank.", "", "SELECT name, price, DENSE_RANK() OVER(ORDER BY price DESC) AS rnk FROM products;"),
        Task("adc-t3", "Assign a strict sequential row number to every customer based on when they registered (ordered by id). Return name and row_num.", "", "SELECT name, ROW_NUMBER() OVER(ORDER BY id ASC) AS row_num FROM customers;"),
        Task("adc-t4", "For each product, show its price and the average price of its entire category. Return name, category, price, and category_avg.", "", "SELECT name, category, price, AVG(price) OVER(PARTITION BY category) AS category_avg FROM products;"),
        Task("adc-t5", "Find the price difference between a product and the cheapest product in its category. Return name, category, price, and diff.", "", "SELECT name, category, price, price - MIN(price) OVER(PARTITION BY category) AS diff FROM products;"),
        Task("adc-t6", "Calculate a running total of product stock within each category, ordered by product id. Return name, category, stock, and running_stock.", "", "SELECT name, category, stock, SUM(stock) OVER(PARTITION BY category ORDER BY id) AS running_stock FROM products;"),
        Task("adc-t7", "Find the previous product's price (ordered by id) within the same category. Return name, category, price, and prev_price.", "", "SELECT name, category, price, LAG(price) OVER(PARTITION BY category ORDER BY id) AS prev_price FROM products;"),
        Task("adc-t8", "Identify the top 2 most expensive products in each category. Use a CTE and a window function. Return category and name.", "", "WITH Ranked AS (SELECT category, name, ROW_NUMBER() OVER(PARTITION BY category ORDER BY price DESC) as rnk FROM products) SELECT category, name FROM Ranked WHERE rnk <= 2;"),
        Task("adc-t9", "Calculate the 3-item moving average of product prices (current row and 2 preceding), ordered by id. Return name, price, and moving_avg.", "", "SELECT name, price, AVG(price) OVER(ORDER BY id ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg FROM products;"),
        Task("adc-t10", "Determine the percentage contribution of each product's stock to its category's total stock. Return name, category, and pct.", "", "SELECT name, category, (CAST(stock AS REAL) / SUM(stock) OVER(PARTITION BY category)) * 100 AS pct FROM products;"),
        Task("adc-t11", "Create a CTE named 'BigOrders' containing order IDs with more than 3 items total. Then select all from it.", "", "WITH BigOrders AS (SELECT order_id FROM order_items GROUP BY order_id HAVING SUM(quantity) > 3) SELECT * FROM BigOrders;"),
        Task("adc-t12", "Use a CTE to calculate the total lifetime spend per customer, then select customers who spent over 500.", "", "WITH Spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS total_spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name) SELECT name, total_spend FROM Spend WHERE total_spend > 500;"),
        Task("adc-t13", "Find the most expensive order (by total value) placed by each customer. Return customer name and max_order_value.", "", "WITH OrderTotals AS (SELECT orders.customer_id, orders.id, SUM(quantity * unit_price) as total FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY orders.id) SELECT customers.name, MAX(total) FROM customers JOIN OrderTotals ON OrderTotals.customer_id = customers.id GROUP BY customers.id, customers.name;"),
        Task("adc-t14", "Divide products into exactly 4 equal-sized price tiers (quartiles). Return name, price, and quartile (1-4).", "", "SELECT name, price, NTILE(4) OVER(ORDER BY price) AS quartile FROM products;"),
        Task("adc-t15", "Use a recursive CTE to generate a sequence of numbers from 1 to 10.", "", "WITH RECURSIVE seq AS (SELECT 1 AS num UNION ALL SELECT num + 1 FROM seq WHERE num < 10) SELECT * FROM seq;"),
        Task("adc-t16", "Find the first order placed by each customer. Return customer name and ordered_at.", "", "WITH RankedOrders AS (SELECT customers.name, orders.ordered_at, ROW_NUMBER() OVER(PARTITION BY customers.id ORDER BY orders.ordered_at ASC) as rnk FROM customers JOIN orders ON orders.customer_id = customers.id) SELECT name, ordered_at FROM RankedOrders WHERE rnk = 1;"),
        Task("adc-t17", "Identify gaps in order IDs (if any exist between MIN and MAX). Use LEAD to find where the next ID is not ID+1.", "", "SELECT id, LEAD(id) OVER(ORDER BY id) AS next_id FROM orders WHERE LEAD(id) OVER(ORDER BY id) != id + 1;"),
        Task("adc-t18", "Find the difference in days between a customer's current order and their previous order. Return customer_id, order_id, and days_since_last.", "", "SELECT customer_id, id, ROUND(julianday(ordered_at) - julianday(LAG(ordered_at) OVER(PARTITION BY customer_id ORDER BY ordered_at)), 1) AS days_since_last FROM orders;"),
        Task("adc-t19", "Calculate a running total of revenue for the entire store, ordered chronologically by order date.", "", "WITH OrderRev AS (SELECT orders.ordered_at, SUM(order_items.quantity * order_items.unit_price) AS rev FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY orders.id, orders.ordered_at) SELECT ordered_at, rev, SUM(rev) OVER(ORDER BY ordered_at) AS running_total FROM OrderRev;"),
        Task("adc-t20", "Find employees and their management hierarchy level. The CEO (manager_id IS NULL) is level 1, direct reports are level 2, etc. Use a Recursive CTE.", "", "WITH RECURSIVE Hierarchy AS (SELECT id, name, manager_id, 1 AS level FROM employees WHERE manager_id IS NULL UNION ALL SELECT e.id, e.name, e.manager_id, h.level + 1 FROM employees e JOIN Hierarchy h ON e.manager_id = h.id) SELECT name, level FROM Hierarchy;"),
    ]),
    Lesson("execution-order", 37, "Query Order", ["WHERE", "GROUP BY", "HAVING", "ORDER BY"], ["orders", "order_items", "customers"], [
        Task("l12-t1", "For delivered orders only, show total revenue per order (as 'order_total', rounded to 2 decimals). Keep only orders with total above 100. Sort by order_total descending.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total FROM orders JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY orders.id HAVING SUM(order_items.quantity * order_items.unit_price) > 100 ORDER BY order_total DESC;"),
        Task("l12-t2", "By country, count delivered orders and keep countries with at least two. Show country and count as 'delivered_orders', sorted by delivered_orders descending then country.", "", "SELECT customers.country, COUNT(orders.id) AS delivered_orders FROM customers JOIN orders ON orders.customer_id = customers.id WHERE orders.status = 'delivered' GROUP BY customers.country HAVING COUNT(orders.id) >= 2 ORDER BY delivered_orders DESC, customers.country;"),
        Task("l12-t3", "Show each customer's total spending (as 'spend', rounded to 2 decimals) for non-cancelled orders, sorted by spend descending. Join customers, orders, and order_items.", "", "SELECT customers.name, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status <> 'cancelled' GROUP BY customers.id, customers.name ORDER BY spend DESC;"),
        Task("l12-t4", "Show order channels with average order total above 75 (as 'avg_total', rounded to 2 decimals). Use a subquery to calculate each order's total first. Sort by avg_total descending.", "", "SELECT orders.channel, ROUND(AVG(order_totals.total), 2) AS avg_total FROM orders JOIN (SELECT order_id, SUM(quantity * unit_price) AS total FROM order_items GROUP BY order_id) AS order_totals ON order_totals.order_id = orders.id GROUP BY orders.channel HAVING AVG(order_totals.total) > 75 ORDER BY avg_total DESC;"),
        Task("l12-t5", "Find active (not discontinued) product categories with more than one product in stock (stock > 0). Show category and count as 'stocked_products', sorted by category.", "", "SELECT category, COUNT(*) AS stocked_products FROM products WHERE discontinued = 0 AND stock > 0 GROUP BY category HAVING COUNT(*) > 1 ORDER BY category;"),
    ]),
    Lesson("indexes-query-plans", 38, "Indexes and Query Plans", ["CREATE INDEX", "EXPLAIN QUERY PLAN"], ["products", "orders", "customers", "order_items"], [
            Task("l34-t1", "Create an index named 'idx_orders_customer_id' on orders(customer_id).", "", "CREATE INDEX idx_orders_customer_id ON orders(customer_id);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_orders_customer_id';"),
            Task("l34-t2", "Create a composite index named 'idx_orders_status_ordered_at' on orders(status, ordered_at).", "", "CREATE INDEX idx_orders_status_ordered_at ON orders(status, ordered_at);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_orders_status_ordered_at';"),
            Task("l34-t3", "Create a unique index named 'idx_customers_name_city' on customers(name, city).", "", "CREATE UNIQUE INDEX idx_customers_name_city ON customers(name, city);", "SELECT name, \"unique\" FROM pragma_index_list('customers') WHERE name = 'idx_customers_name_city';"),
            Task("l34-t4", "Use EXPLAIN QUERY PLAN to see how SQLite resolves a customer lookup by id.", "", "EXPLAIN QUERY PLAN SELECT * FROM customers WHERE id = 1;"),
            Task("l34-t5", "Create an index named 'idx_order_items_product_id' on order_items(product_id) to speed up product joins.", "", "CREATE INDEX idx_order_items_product_id ON order_items(product_id);", "SELECT name, tbl_name FROM sqlite_master WHERE type = 'index' AND name = 'idx_order_items_product_id';"),
        ]),
    Lesson("interview-filters", 39, "Interview Filtering Patterns", ["BETWEEN", "NOT IN", "multi-condition"], ["products", "customers", "orders"], [
            Task("l20-t1", "Find non-discontinued products priced between 25 and 90 inclusive. Show name and price, sorted by price then name.", "", "SELECT name, price FROM products WHERE price BETWEEN 25 AND 90 AND discontinued = 0 ORDER BY price, name;"),
            Task("l20-t2", "Find customers who are not bronze tier and signed up on or after March 2023. Show name, tier, and signup_date, sorted by signup_date then name.", "", "SELECT name, tier, signup_date FROM customers WHERE tier <> 'bronze' AND signup_date >= '2023-03-01' ORDER BY signup_date, name;"),
            Task("l20-t3", "Find non-cancelled orders placed through web or mobile. Show id, status, and channel, sorted by id.", "", "SELECT id, status, channel FROM orders WHERE status <> 'cancelled' AND channel IN ('web', 'mobile') ORDER BY id;"),
            Task("l20-t4", "Find products whose name contains 'Desk' or whose category is 'Office'. Show name and category, sorted by name.", "", "SELECT name, category FROM products WHERE name LIKE '%Desk%' OR category = 'Office' ORDER BY name;"),
            Task("l20-t5", "Find gold-tier customers from India or Singapore. Show name, country, and tier, sorted by name.", "", "SELECT name, country, tier FROM customers WHERE tier = 'gold' AND country IN ('India', 'Singapore') ORDER BY name;"),
        ]),
    Lesson("insert", 40, "INSERT Rows", ["INSERT"], ["products", "customers", "orders", "order_items"], [
        Task("l13-t1", "Insert a new Office product with id 13, named 'Cable Clips', priced 7.50, stock 90, rating 4.2, not discontinued.", "", "INSERT INTO products (id, name, category, price, stock, rating, discontinued) VALUES (13, 'Cable Clips', 'Office', 7.50, 90, 4.2, 0);", "SELECT name, category, price, stock, rating, discontinued FROM products WHERE id = 13;"),
        Task("l13-t2", "Insert a new customer with id 9, named 'Hana Lee', from Seoul, South Korea, signed up on 2024-04-15, bronze tier, no referrer.", "", "INSERT INTO customers (id, name, city, country, signup_date, tier, referrer_id) VALUES (9, 'Hana Lee', 'Seoul', 'South Korea', '2024-04-15', 'bronze', NULL);", "SELECT name, city, country, signup_date, tier, referrer_id FROM customers WHERE id = 9;"),
        Task("l13-t3", "Insert a new order with id 111 for customer 1, ordered on 2024-04-16, status processing, channel web.", "", "INSERT INTO orders (id, customer_id, ordered_at, status, channel) VALUES (111, 1, '2024-04-16', 'processing', 'web');", "SELECT id, customer_id, ordered_at, status, channel FROM orders WHERE id = 111;"),
        Task("l13-t4", "Insert two order items for order 101: id 1018 for product 2 quantity 1 at 42.50, and id 1019 for product 5 quantity 2 at 12.75.", "", "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) VALUES (1018, 101, 2, 1, 42.50), (1019, 101, 5, 2, 12.75);", "SELECT order_id, product_id, quantity, unit_price FROM order_items WHERE id IN (1018, 1019) ORDER BY product_id;"),
    ]),
    Lesson("update", 41, "UPDATE Rows", ["UPDATE", "SET"], ["products", "orders", "support_tickets"], [
        Task("l14-t1", "Mark product 12 as active (discontinued = 0) and set its stock to 25.", "", "UPDATE products SET discontinued = 0, stock = 25 WHERE id = 12;", "SELECT stock, discontinued FROM products WHERE id = 12;"),
        Task("l14-t2", "Increase all Office product prices by 2.00.", "", "UPDATE products SET price = price + 2.00 WHERE category = 'Office';", "SELECT name, price FROM products WHERE category = 'Office' ORDER BY name;"),
        Task("l14-t3", "Change order 105 status to 'shipped'.", "", "UPDATE orders SET status = 'shipped' WHERE id = 105;", "SELECT id, status FROM orders WHERE id = 105;"),
        Task("l14-t4", "Close all open high-priority support tickets and set their resolved_at to '2024-04-10'.", "", "UPDATE support_tickets SET status = 'closed', resolved_at = '2024-04-10' WHERE status = 'open' AND priority = 'high';", "SELECT id, priority, status, resolved_at FROM support_tickets WHERE priority = 'high' ORDER BY id;"),
    ]),
    Lesson("delete", 42, "DELETE Rows", ["DELETE"], ["products", "orders", "support_tickets"], [
        Task("l15-t1", "Delete only discontinued products that have zero stock.", "", "DELETE FROM products WHERE discontinued = 1 AND stock = 0;", "SELECT id, name FROM products ORDER BY id;"),
        Task("l15-t2", "Delete cancelled order 103: first delete its support ticket, then its order items, then the order itself.", "", "DELETE FROM support_tickets WHERE order_id = 103; DELETE FROM order_items WHERE order_id = 103; DELETE FROM orders WHERE id = 103 AND status = 'cancelled';", "SELECT id FROM orders WHERE id = 103 UNION ALL SELECT order_id FROM order_items WHERE order_id = 103 UNION ALL SELECT order_id FROM support_tickets WHERE order_id = 103;"),
        Task("l15-t3", "Delete closed low-priority support tickets.", "", "DELETE FROM support_tickets WHERE status = 'closed' AND priority = 'low';", "SELECT id, priority, status FROM support_tickets ORDER BY id;"),
        Task("l15-t4", "Delete order items for Fitness products with rating below 4.0, then delete those products.", "", "DELETE FROM order_items WHERE product_id IN (SELECT id FROM products WHERE category = 'Fitness' AND rating < 4.0); DELETE FROM products WHERE category = 'Fitness' AND rating < 4.0;", "SELECT id, name, category, rating FROM products ORDER BY id;"),
    ]),
    Lesson("create-table", 43, "CREATE TABLE", ["CREATE TABLE", "types"], ["products"], [
        Task("l16-t1", "Create a suppliers table with columns: id (INTEGER PRIMARY KEY), name (TEXT NOT NULL), country (TEXT NOT NULL), and active (INTEGER NOT NULL DEFAULT 1).", "", "CREATE TABLE suppliers (id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1);", "SELECT name, type, \"notnull\", dflt_value, pk FROM pragma_table_info('suppliers') ORDER BY cid;"),
        Task("l16-t2", "Create a product_reviews table with: id (INTEGER PRIMARY KEY), product_id (INTEGER NOT NULL, FK to products), rating (INTEGER NOT NULL), and comment (TEXT, nullable).", "", "CREATE TABLE product_reviews (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), rating INTEGER NOT NULL, comment TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('product_reviews') ORDER BY cid;"),
        Task("l16-t3", "Create a coupons table with: id (INTEGER PRIMARY KEY), code (TEXT NOT NULL UNIQUE), percent_off (INTEGER NOT NULL), and expires_at (TEXT, nullable).", "", "CREATE TABLE coupons (id INTEGER PRIMARY KEY, code TEXT NOT NULL UNIQUE, percent_off INTEGER NOT NULL, expires_at TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('coupons') ORDER BY cid;"),
        Task("l16-t4", "Create an inventory_audits table with: id (INTEGER PRIMARY KEY), product_id (INTEGER NOT NULL, FK to products), counted_at (TEXT NOT NULL), counted_stock (INTEGER NOT NULL), and note (TEXT, nullable).", "", "CREATE TABLE inventory_audits (id INTEGER PRIMARY KEY, product_id INTEGER NOT NULL REFERENCES products(id), counted_at TEXT NOT NULL, counted_stock INTEGER NOT NULL, note TEXT);", "SELECT name, type, \"notnull\", pk FROM pragma_table_info('inventory_audits') ORDER BY cid;"),
    ]),
    Lesson("alter-table", 44, "ALTER TABLE", ["ALTER TABLE"], ["products", "customers"], [
        Task("l17-t1", "Add a reorder_level INTEGER NOT NULL column to products with default 10.", "", "ALTER TABLE products ADD COLUMN reorder_level INTEGER NOT NULL DEFAULT 10;", "SELECT name, type, \"notnull\", dflt_value FROM pragma_table_info('products') WHERE name = 'reorder_level';"),
        Task("l17-t2", "Add a marketing_opt_in INTEGER NOT NULL column to customers with default 0.", "", "ALTER TABLE customers ADD COLUMN marketing_opt_in INTEGER NOT NULL DEFAULT 0;", "SELECT name, type, \"notnull\", dflt_value FROM pragma_table_info('customers') WHERE name = 'marketing_opt_in';"),
        Task("l17-t3", "Rename the support_tickets table to helpdesk_tickets.", "", "ALTER TABLE support_tickets RENAME TO helpdesk_tickets;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name IN ('support_tickets', 'helpdesk_tickets') ORDER BY name;"),
        Task("l17-t4", "Rename the products 'stock' column to 'units_in_stock'.", "", "ALTER TABLE products RENAME COLUMN stock TO units_in_stock;", "SELECT name FROM pragma_table_info('products') WHERE name IN ('stock', 'units_in_stock') ORDER BY name;"),
    ]),
    Lesson("drop-table", 45, "DROP TABLE", ["DROP TABLE", "IF EXISTS"], ["support_tickets", "shipments"], [
        Task("l18-t1", "Drop the support_tickets table.", "", "DROP TABLE support_tickets;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'support_tickets';"),
        Task("l18-t2", "Drop the shipments table only if it exists.", "", "DROP TABLE IF EXISTS shipments;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'shipments';"),
        Task("l18-t3", "Create a table named scratch with columns id (INTEGER PRIMARY KEY) and note (TEXT), then drop it.", "", "CREATE TABLE scratch (id INTEGER PRIMARY KEY, note TEXT); DROP TABLE scratch;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'scratch';"),
        Task("l18-t4", "Drop the order_items table.", "", "DROP TABLE order_items;", "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'order_items';"),
    ]),
    Lesson("insert-select", 46, "CREATE AS & INSERT SELECT", ["CREATE TABLE AS", "INSERT INTO SELECT"], ["orders", "products"], [
        Task("l36i-t1", "Create a new table named 'archived_orders' containing all columns for orders where status is 'cancelled'.", "", "CREATE TABLE archived_orders AS SELECT * FROM orders WHERE status = 'cancelled';", "SELECT name FROM sqlite_master WHERE type='table' AND name='archived_orders';"),
        Task("l36i-t2", "Create a table 'product_summary' with columns 'category' and 'total_stock' by aggregating the products table.", "", "CREATE TABLE product_summary AS SELECT category, SUM(stock) AS total_stock FROM products GROUP BY category;", "SELECT name FROM sqlite_master WHERE type='table' AND name='product_summary';"),
        Task("l36i-t3", "Assume a table 'high_value_customers(id, name)' exists. Insert customers from 'India' into it using INSERT INTO SELECT. (Create it first in your query).", "", "CREATE TABLE high_value_customers (id INTEGER, name TEXT); INSERT INTO high_value_customers SELECT id, name FROM customers WHERE country = 'India';", "SELECT * FROM high_value_customers ORDER BY id;"),
        Task("l36i-t4", "Create a table 'employee_directory' containing just 'name' and 'team' from the employees table, ordered by name.", "", "CREATE TABLE employee_directory AS SELECT name, team FROM employees ORDER BY name;", "SELECT name FROM sqlite_master WHERE type='table' AND name='employee_directory';"),
    ]),
    Lesson("constraints-not-null-default", 47, "Constraints: NOT NULL & DEFAULT", ["NOT NULL", "DEFAULT", "CREATE TABLE"], [], [
        Task("l40-t1", "Create a table 'events' with columns 'id' (INTEGER) and 'name' (TEXT). Ensure 'name' cannot be NULL.", "", "CREATE TABLE events (id INTEGER, name TEXT NOT NULL);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='events';"),
        Task("l40-t2", "Create a table 'audit_logs' with 'id' (INTEGER), 'action' (TEXT), and 'logged_at' (TEXT). Make 'logged_at' default to CURRENT_TIMESTAMP.", "", "CREATE TABLE audit_logs (id INTEGER, action TEXT, logged_at TEXT DEFAULT CURRENT_TIMESTAMP);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='audit_logs';"),
        Task("l40-t3", "Create a table 'users_temp' with 'id' (INTEGER), 'email' (TEXT NOT NULL), and 'is_active' (INTEGER DEFAULT 1).", "", "CREATE TABLE users_temp (id INTEGER, email TEXT NOT NULL, is_active INTEGER DEFAULT 1);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='users_temp';"),
        Task("l40-t4", "Insert a row into 'events' with id=1 and name='login'. The table is created for you in the starter.", "CREATE TABLE events (id INTEGER, name TEXT NOT NULL);\n\n-- Write your insert below\n", "CREATE TABLE events (id INTEGER, name TEXT NOT NULL);\nINSERT INTO events (id, name) VALUES (1, 'login');", "SELECT * FROM events;"),
        Task("l40-t5", "Insert a row into 'users_temp' specifying only the 'email' ('test@test.com'). Let 'id' be NULL and 'is_active' use its default.", "CREATE TABLE users_temp (id INTEGER, email TEXT NOT NULL, is_active INTEGER DEFAULT 1);\n\n-- Write your insert below\n", "CREATE TABLE users_temp (id INTEGER, email TEXT NOT NULL, is_active INTEGER DEFAULT 1);\nINSERT INTO users_temp (email) VALUES ('test@test.com');", "SELECT * FROM users_temp;"),
    ]),
    Lesson("constraints-unique-check", 48, "Constraints: UNIQUE & CHECK", ["UNIQUE", "CHECK"], [], [
        Task("l41-t1", "Create a table 'coupons' with 'code' (TEXT) and 'discount' (REAL). Ensure 'code' is UNIQUE.", "", "CREATE TABLE coupons (code TEXT UNIQUE, discount REAL);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='coupons';"),
        Task("l41-t2", "Create a table 'subscriptions' with 'email' (TEXT) and 'plan' (TEXT). Add a UNIQUE constraint covering both columns together (table-level constraint).", "", "CREATE TABLE subscriptions (email TEXT, plan TEXT, UNIQUE(email, plan));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='subscriptions';"),
        Task("l41-t3", "Create a table 'products_new' with 'price' (REAL). Add a CHECK constraint to ensure price > 0.", "", "CREATE TABLE products_new (price REAL CHECK(price > 0));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='products_new';"),
        Task("l41-t4", "Create 'users_v2' with 'email' (TEXT). Add a CHECK constraint validating the email contains an '@' symbol.", "", "CREATE TABLE users_v2 (email TEXT CHECK(email LIKE '%@%'));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='users_v2';"),
        Task("l41-t5", "Create 'orders_v2' with 'status' (TEXT). Add a CHECK constraint ensuring status is either 'pending', 'shipped', or 'delivered'.", "", "CREATE TABLE orders_v2 (status TEXT CHECK(status IN ('pending', 'shipped', 'delivered')));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='orders_v2';"),
    ]),
    Lesson("constraints-keys", 49, "Constraints: Keys", ["PRIMARY KEY", "FOREIGN KEY", "AUTOINCREMENT"], ["customers"], [
        Task("l42-t1", "Create a table 'tags' with 'id' as an INTEGER PRIMARY KEY.", "", "CREATE TABLE tags (id INTEGER PRIMARY KEY);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='tags';"),
        Task("l42-t2", "Create a table 'logs' with 'id' as INTEGER PRIMARY KEY AUTOINCREMENT.", "", "CREATE TABLE logs (id INTEGER PRIMARY KEY AUTOINCREMENT);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='logs';"),
        Task("l42-t3", "Create a table 'user_roles' with 'user_id' (INTEGER) and 'role_id' (INTEGER). Define a composite PRIMARY KEY on (user_id, role_id).", "", "CREATE TABLE user_roles (user_id INTEGER, role_id INTEGER, PRIMARY KEY(user_id, role_id));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='user_roles';"),
        Task("l42-t4", "Create a table 'orders_fk' with 'customer_id' (INTEGER). Add a FOREIGN KEY referencing the 'customers(id)'.", "", "CREATE TABLE orders_fk (customer_id INTEGER, FOREIGN KEY(customer_id) REFERENCES customers(id));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='orders_fk';"),
        Task("l42-t5", "Create 'orders_fk2' with a FOREIGN KEY on 'customer_id' referencing 'customers(id)' ON DELETE CASCADE.", "", "CREATE TABLE orders_fk2 (customer_id INTEGER, FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='orders_fk2';"),
    ]),
    Lesson("views", 50, "Database Views", ["CREATE VIEW", "DROP VIEW"], ["orders", "order_items", "products"], [
        Task("l43-t1", "Create a view named 'premium_customers' that selects all customers from 'India'.", "", "CREATE VIEW premium_customers AS SELECT * FROM customers WHERE country = 'India';", "SELECT sql FROM sqlite_master WHERE type='view' AND name='premium_customers';"),
        Task("l43-t2", "Query all data from the 'premium_customers' view you just created. The view is pre-created in the starter.", "CREATE VIEW premium_customers AS SELECT * FROM customers WHERE country = 'India';\n\n-- Write your query below\n", "CREATE VIEW premium_customers AS SELECT * FROM customers WHERE country = 'India';\nSELECT * FROM premium_customers;", "SELECT * FROM premium_customers;"),
        Task("l43-t3", "Create a view 'daily_sales' containing 'ordered_at' (date only using substr) and 'total_orders' (count of orders).", "", "CREATE VIEW daily_sales AS SELECT substr(ordered_at, 1, 10) AS ordered_at, COUNT(*) AS total_orders FROM orders GROUP BY substr(ordered_at, 1, 10);", "SELECT sql FROM sqlite_master WHERE type='view' AND name='daily_sales';"),
        Task("l43-t4", "Create a view 'product_revenue' showing product 'name' and total 'revenue' (sum of quantity * price) from order_items joined with products.", "", "CREATE VIEW product_revenue AS SELECT products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name;", "SELECT sql FROM sqlite_master WHERE type='view' AND name='product_revenue';"),
        Task("l43-t5", "Drop the view named 'old_view'. It is created for you in the starter.", "CREATE VIEW old_view AS SELECT * FROM orders;\n\n-- Write your drop below\n", "CREATE VIEW old_view AS SELECT * FROM orders;\nDROP VIEW old_view;", "SELECT name FROM sqlite_master WHERE type='view' AND name='old_view';"),
    ]),
    Lesson("indexes", 51, "Indexes", ["CREATE INDEX", "UNIQUE INDEX", "DROP INDEX"], ["customers", "orders"], [
        Task("l44-t1", "Create an index named 'idx_orders_status' on the 'status' column of the 'orders' table.", "", "CREATE INDEX idx_orders_status ON orders(status);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_orders_status';"),
        Task("l44-t2", "Create a UNIQUE index named 'idx_customers_email' on the 'email' column of the 'customers' table.", "", "CREATE UNIQUE INDEX idx_customers_email ON customers(email);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_customers_email';"),
        Task("l44-t3", "Create a composite index named 'idx_orders_cust_status' on the 'customer_id' and 'status' columns of 'orders'.", "", "CREATE INDEX idx_orders_cust_status ON orders(customer_id, status);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_orders_cust_status';"),
        Task("l44-t4", "Create an index 'idx_orders_date' on the 'ordered_at' column in DESCENDING order.", "", "CREATE INDEX idx_orders_date ON orders(ordered_at DESC);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_orders_date';"),
        Task("l44-t5", "Drop the index named 'idx_old'. It is created for you in the starter.", "CREATE INDEX idx_old ON orders(id);\n\n-- Write your drop below\n", "CREATE INDEX idx_old ON orders(id);\nDROP INDEX idx_old;", "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_old';"),
    ]),
    Lesson("injection", 52, "Security: SQL Injection", ["hacker mode", "authentication bypass", "UNION payloads"], ["customers"], [
        Task("l47-t1", "Hacker Mode: Write the query that results from injecting `' OR '1'='1' --` into a login form. Select everything from customers where name is 'admin' OR '1'='1' followed by a comment.", "", "SELECT * FROM customers WHERE name = 'admin' OR '1'='1' --;", "SELECT * FROM customers;"),
        Task("l47-t2", "Hacker Mode: Piggy-backing commands. Write the resulting query when dropping a table via injection: Select name from products where id = 1, then end the statement with ;, then DROP the 'orders' table, then add a comment --.", "", "SELECT name FROM products WHERE id = 1; DROP TABLE orders; --;", "SELECT sql FROM sqlite_master WHERE type='table' AND name='orders';"),
        Task("l47-t3", "Hacker Mode: Data Exfiltration via UNION. Write the query: Select name, price from products where category = 'Shoes', then UNION SELECT email, 1 from customers, followed by a comment --.", "", "SELECT name, price FROM products WHERE category = 'Shoes' UNION SELECT email, 1 FROM customers --;", ""),
    ]),
    Lesson("ddl-capstone", 53, "DDL & Admin: Interview Capstone", ["Hint-Free", "Data Modeling"], ["customers", "orders", "products"], [
        Task("dc-t1", "Create a table 'sessions' with 'id' (TEXT) and 'user_id' (INTEGER).", "", "CREATE TABLE sessions (id TEXT, user_id INTEGER);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='sessions';"),
        Task("dc-t2", "Create a table 'metrics' ensuring 'name' cannot be null.", "", "CREATE TABLE metrics (name TEXT NOT NULL, value REAL);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='metrics';"),
        Task("dc-t3", "Create 'logs_archive' by copying all data from 'logs' table (which doesn't exist here, assume copy from 'orders'). Create table AS SELECT all orders.", "", "CREATE TABLE orders_archive AS SELECT * FROM orders;", "SELECT sql FROM sqlite_master WHERE type='table' AND name='orders_archive';"),
        Task("dc-t4", "Add a new column 'discount' (REAL) to the existing 'products' table.", "CREATE TABLE products (id INTEGER, price REAL);\n\n-- Write your alter below\n", "CREATE TABLE products (id INTEGER, price REAL);\nALTER TABLE products ADD COLUMN discount REAL;", "SELECT sql FROM sqlite_master WHERE type='table' AND name='products';"),
        Task("dc-t5", "Rename the 'products' table to 'inventory'.", "CREATE TABLE products (id INTEGER, price REAL);\n\n-- Write your alter below\n", "CREATE TABLE products (id INTEGER, price REAL);\nALTER TABLE products RENAME TO inventory;", "SELECT name FROM sqlite_master WHERE type='table' AND name='inventory';"),
        Task("dc-t6", "Drop the table 'old_data' permanently.", "CREATE TABLE old_data (id INTEGER);\n\n-- Write your drop below\n", "CREATE TABLE old_data (id INTEGER);\nDROP TABLE old_data;", "SELECT name FROM sqlite_master WHERE type='table' AND name='old_data';"),
        Task("dc-t7", "Insert a new product into 'products'. ID is 999, name is 'Gadget', price is 49.99, stock is 100, category is 'Misc'.", "CREATE TABLE products (id INTEGER, name TEXT, price REAL, stock INTEGER, category TEXT);\n\n-- Write your insert below\n", "CREATE TABLE products (id INTEGER, name TEXT, price REAL, stock INTEGER, category TEXT);\nINSERT INTO products (id, name, price, stock, category) VALUES (999, 'Gadget', 49.99, 100, 'Misc');", "SELECT * FROM products WHERE id = 999;"),
        Task("dc-t8", "Update all products in the 'Electronics' category to increase their price by 10%.", "CREATE TABLE products (id INTEGER, name TEXT, price REAL, category TEXT);\nINSERT INTO products VALUES (1, 'TV', 100, 'Electronics');\n\n-- Write your update below\n", "CREATE TABLE products (id INTEGER, name TEXT, price REAL, category TEXT);\nINSERT INTO products VALUES (1, 'TV', 100, 'Electronics');\nUPDATE products SET price = price * 1.10 WHERE category = 'Electronics';", "SELECT price FROM products WHERE id = 1;"),
        Task("dc-t9", "Delete all orders that have a status of 'cancelled'.", "CREATE TABLE orders (id INTEGER, status TEXT);\nINSERT INTO orders VALUES (1, 'cancelled'), (2, 'pending');\n\n-- Write your delete below\n", "CREATE TABLE orders (id INTEGER, status TEXT);\nINSERT INTO orders VALUES (1, 'cancelled'), (2, 'pending');\nDELETE FROM orders WHERE status = 'cancelled';", "SELECT * FROM orders;"),
        Task("dc-t10", "Create a view 'active_customers' showing customers who have placed at least one order.", "", "CREATE VIEW active_customers AS SELECT DISTINCT customers.* FROM customers JOIN orders ON orders.customer_id = customers.id;", "SELECT sql FROM sqlite_master WHERE type='view' AND name='active_customers';"),
        Task("dc-t11", "Create an index on the 'email' column of the 'customers' table to speed up logins.", "", "CREATE INDEX idx_customers_email ON customers(email);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_customers_email';"),
        Task("dc-t12", "Create a UNIQUE index on the 'phone' column in 'customers' to prevent duplicates.", "", "CREATE UNIQUE INDEX idx_customers_phone ON customers(phone);", "SELECT sql FROM sqlite_master WHERE type='index' AND name='idx_customers_phone';"),
        Task("dc-t13", "Create a table 'payments' with a composite PRIMARY KEY consisting of 'order_id' and 'transaction_id'.", "", "CREATE TABLE payments (order_id INTEGER, transaction_id TEXT, amount REAL, PRIMARY KEY(order_id, transaction_id));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='payments';"),
        Task("dc-t14", "Create a table 'shipments_v2' ensuring 'carrier' defaults to 'USPS'.", "", "CREATE TABLE shipments_v2 (id INTEGER, carrier TEXT DEFAULT 'USPS');", "SELECT sql FROM sqlite_master WHERE type='table' AND name='shipments_v2';"),
        Task("dc-t15", "Create a table 'accounts' ensuring 'balance' cannot drop below 0 using a CHECK constraint.", "", "CREATE TABLE accounts (id INTEGER, balance REAL CHECK(balance >= 0));", "SELECT sql FROM sqlite_master WHERE type='table' AND name='accounts';"),
        Task("dc-t16", "Create a table 'profiles' with an AUTOINCREMENT primary key 'id'.", "", "CREATE TABLE profiles (id INTEGER PRIMARY KEY AUTOINCREMENT, bio TEXT);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='profiles';"),
        Task("dc-t17", "Hacker Mode: Bypass an authentication query. Write the resulting query if you inject `' OR 1=1 --` into the username field of `SELECT * FROM admins WHERE username = '[INPUT]'`.", "", "SELECT * FROM admins WHERE username = '' OR 1=1 --';", "SELECT 1;"),
        Task("dc-t18", "Drop the view 'active_customers' permanently.", "CREATE VIEW active_customers AS SELECT 1;\n\n-- Write your drop below\n", "CREATE VIEW active_customers AS SELECT 1;\nDROP VIEW active_customers;", "SELECT name FROM sqlite_master WHERE type='view' AND name='active_customers';"),
        Task("dc-t19", "Insert a new row into 'products', pulling the data directly from an existing 'products_staging' table.", "CREATE TABLE products (id INTEGER, name TEXT);\nCREATE TABLE products_staging (id INTEGER, name TEXT);\nINSERT INTO products_staging VALUES (1, 'Test');\n\n-- Write your insert below\n", "CREATE TABLE products (id INTEGER, name TEXT);\nCREATE TABLE products_staging (id INTEGER, name TEXT);\nINSERT INTO products_staging VALUES (1, 'Test');\nINSERT INTO products SELECT * FROM products_staging;", "SELECT * FROM products;"),
        Task("dc-t20", "Create a table 'order_history' with a FOREIGN KEY 'order_id' referencing 'orders(id)' ON DELETE CASCADE.", "", "CREATE TABLE order_history (id INTEGER, order_id INTEGER, action TEXT, FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE);", "SELECT sql FROM sqlite_master WHERE type='table' AND name='order_history';"),
    ]),
    Lesson("leetcode-patterns", 54, "Classic Interview Patterns", ["second highest", "duplicates", "gaps"], ["products", "customers", "orders"], [
            Task("l32-t1", "Find the second most expensive product price (as 'second_highest_price'). Use a subquery.", "", "SELECT MAX(price) AS second_highest_price FROM products WHERE price < (SELECT MAX(price) FROM products);"),
            Task("l32-t2", "Find countries that have more than one customer. Show country and count as 'customer_count', sorted by country.", "", "SELECT country, COUNT(*) AS customer_count FROM customers GROUP BY country HAVING COUNT(*) > 1 ORDER BY country;"),
            Task("l32-t3", "Find customers with consecutive orders less than 40 days apart. Use LAG to get previous_order_at. Show distinct name, sorted by name.", "", "SELECT DISTINCT name FROM (SELECT customers.name, ordered_at, LAG(ordered_at) OVER (PARTITION BY customers.id ORDER BY ordered_at) AS previous_order_at FROM customers JOIN orders ON orders.customer_id = customers.id) AS ordered WHERE previous_order_at IS NOT NULL AND julianday(ordered_at) - julianday(previous_order_at) < 40 ORDER BY name;"),
            Task("l32-t4", "Find product pairs in the same category with the same rounded rating (ROUND to 0 decimals, a.id < b.id). Show product_a, product_b, category, and rating. Sort by category then product_a.", "", "SELECT a.name AS product_a, b.name AS product_b, a.category, a.rating FROM products a JOIN products b ON a.category = b.category AND a.id < b.id AND ROUND(a.rating, 0) = ROUND(b.rating, 0) ORDER BY a.category, product_a;"),
            Task("l32-t5", "Return the first order for every customer who has ordered. Use ROW_NUMBER in a subquery. Show customer_id, first_order_id, and ordered_at, sorted by customer_id.", "", "SELECT customer_id, id AS first_order_id, ordered_at FROM (SELECT customer_id, id, ordered_at, ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at, id) AS rn FROM orders) AS ranked WHERE rn = 1 ORDER BY customer_id;"),
        ]),
    Lesson("business-analytics", 55, "Business Intelligence SQL", ["JOIN", "arithmetic", "business-logic"], ["customers", "orders", "order_items", "products", "shipments"], [
            Task("l36-t1", "Calculate the total revenue (quantity × unit_price) per customer city. Show city and 'total_revenue' (rounded to 2 decimals), sorted by total_revenue descending.", "", "SELECT customers.city, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS total_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.city ORDER BY total_revenue DESC;"),
            Task("l36-t2", "For delivered orders, show the order id and the 'net_amount' (sum of item revenue + shipping_cost). Sort by net_amount descending.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price) + shipments.shipping_cost, 2) AS net_amount FROM orders JOIN order_items ON order_items.order_id = orders.id JOIN shipments ON shipments.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY orders.id, shipments.shipping_cost ORDER BY net_amount DESC;"),
            Task("l36-t3", "Find the average discount per product category. Discount is (products.price - order_items.unit_price). Show category and 'avg_discount' (rounded to 2 decimals), sorted by avg_discount descending.", "", "SELECT products.category, ROUND(AVG(products.price - order_items.unit_price), 2) AS avg_discount FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.category ORDER BY avg_discount DESC;"),
            Task("l36-t4", "Calculate each customer's 'loyalty_points': 5 points per item purchased + 1 point for every 10 currency spent. Show name and 'points' (as integer), sorted by points descending.", "", "SELECT customers.name, CAST(SUM(order_items.quantity) * 5 + SUM(order_items.quantity * order_items.unit_price) / 10 AS INTEGER) AS points FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name ORDER BY points DESC;"),
            Task("l36-t5", "For each category, show 'inventory_value' (sum of stock × price) and 'actual_revenue' (sum of items). Include categories with no sales. Sort by category.", "", "SELECT products.category, ROUND(SUM(products.stock * products.price), 2) AS inventory_value, ROUND(COALESCE(SUM(order_items.quantity * order_items.unit_price), 0), 2) AS actual_revenue FROM products LEFT JOIN order_items ON order_items.product_id = products.id GROUP BY products.category ORDER BY products.category;"),
            Task("l36-t6", "Find the Average Order Value (AOV) for each customer tier. AOV is total revenue divided by unique order count. Show tier and 'avg_order_value' (rounded to 2 decimals), sorted by avg_order_value descending.", "", "SELECT customers.tier, ROUND(SUM(order_items.quantity * order_items.unit_price) / CAST(COUNT(DISTINCT orders.id) AS REAL), 2) AS avg_order_value FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.tier ORDER BY avg_order_value DESC;"),
            Task("l36-t7", "Calculate 'carrier_cost_per_unit': for each carrier, find the total shipping cost divided by total quantity of items delivered. Show carrier and 'cost_per_unit' (rounded to 2 decimals), sorted by cost_per_unit.", "", "SELECT shipments.carrier, ROUND(SUM(shipments.shipping_cost) / SUM(order_items.quantity), 2) AS cost_per_unit FROM shipments JOIN order_items ON order_items.order_id = shipments.order_id GROUP BY shipments.carrier ORDER BY cost_per_unit;"),
            Task("l36-t8", "Find 'top_rated_revenue' products: those with a rating above 4.5 and total revenue exceeding 150. Show name, rating, and revenue, sorted by revenue descending.", "", "SELECT products.name, products.rating, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id WHERE products.rating > 4.5 GROUP BY products.id, products.name, products.rating HAVING revenue > 150 ORDER BY revenue DESC;"),
            Task("l36-t9", "Calculate 'referral_revenue': for each customer who referred someone, find the total revenue generated by their referrals. Show referrer name and 'referral_revenue', sorted by referral_revenue descending.", "", "SELECT r.name, ROUND(SUM(oi.quantity * oi.unit_price), 2) AS referral_revenue FROM customers r JOIN customers c ON c.referrer_id = r.id JOIN orders o ON o.customer_id = c.id JOIN order_items oi ON oi.order_id = o.id GROUP BY r.id, r.name ORDER BY referral_revenue DESC;"),
            Task("l36-t10", "Show 'stock_to_sales_ratio': for each product, show stock divided by total units sold. Show name, stock, and 'ratio' (rounded to 2 decimals), sorted by ratio descending.", "", "SELECT products.name, products.stock, ROUND(CAST(products.stock AS REAL) / SUM(order_items.quantity), 2) AS ratio FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name, products.stock ORDER BY ratio DESC;"),
        ]),
    Lesson("final-interview-sets", 56, "Final Interview Sets", ["multi-step", "analytics", "business SQL"], ["customers", "orders", "order_items", "products", "shipments", "support_tickets"], [
            Task("l35-t1", "Find the top three customers by delivered revenue (only delivered orders). Show customer name and delivered_revenue (rounded to 2 decimals), sorted by delivered_revenue descending. Use LIMIT 3.", "", "SELECT customers.name, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS delivered_revenue FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY customers.id, customers.name ORDER BY delivered_revenue DESC LIMIT 3;"),
            Task("l35-t2", "For each month, show total orders (as 'orders_count'), total revenue, and count of delivered orders (as 'delivered_orders'). Use substr for month. Sort by month.", "", "SELECT substr(orders.ordered_at, 1, 7) AS month, COUNT(DISTINCT orders.id) AS orders_count, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS revenue, COUNT(DISTINCT CASE WHEN orders.status = 'delivered' THEN orders.id END) AS delivered_orders FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY month ORDER BY month;"),
            Task("l35-t3", "Find products with above-average product revenue. Use a CTE 'product_revenue'. Show name and revenue (rounded to 2 decimals), sorted by revenue descending.", "", "WITH product_revenue AS (SELECT products.id, products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name) SELECT name, ROUND(revenue, 2) AS revenue FROM product_revenue WHERE revenue > (SELECT AVG(revenue) FROM product_revenue) ORDER BY revenue DESC;"),
            Task("l35-t4", "Find customers who have both a support ticket and delivered revenue above 100. Use a CTE 'delivered_spend' and EXISTS. Show name and spend (rounded to 2 decimals), sorted by spend descending.", "", "WITH delivered_spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id WHERE orders.status = 'delivered' GROUP BY customers.id, customers.name) SELECT name, ROUND(spend, 2) AS spend FROM delivered_spend WHERE spend > 100 AND EXISTS (SELECT 1 FROM support_tickets WHERE support_tickets.customer_id = delivered_spend.id) ORDER BY spend DESC;"),
            Task("l35-t5", "Build an operations dashboard by order: show order id, order_total (rounded to 2 decimals), shipment_state ('delivered'/'in_transit'/'not_shipped'), and ticket_count. Use LEFT JOINs for shipments and support_tickets. Sort by order id.", "", "SELECT orders.id, ROUND(SUM(order_items.quantity * order_items.unit_price), 2) AS order_total, CASE WHEN shipments.delivered_at IS NOT NULL THEN 'delivered' WHEN shipments.shipped_at IS NOT NULL THEN 'in_transit' ELSE 'not_shipped' END AS shipment_state, COUNT(DISTINCT support_tickets.id) AS ticket_count FROM orders JOIN order_items ON order_items.order_id = orders.id LEFT JOIN shipments ON shipments.order_id = orders.id LEFT JOIN support_tickets ON support_tickets.order_id = orders.id GROUP BY orders.id, shipments.delivered_at, shipments.shipped_at ORDER BY orders.id;"),
        ]),
    Lesson("mixed-bag-capstone", 57, "Mixed Bag: Ultimate Capstone", ["Hint-Free", "Advanced Business Logic"], ["customers", "orders", "order_items", "products", "shipments", "employees", "support_tickets"], [
        Task("mbc-t1", "Find the customer name who has spent the highest total amount across all their orders. Return name and total_spend.", "", "SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS total_spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name ORDER BY total_spend DESC LIMIT 1;"),
        Task("mbc-t2", "Identify the product name that has generated the highest total revenue (quantity * unit_price). Return name and revenue.", "", "SELECT products.name, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.id, products.name ORDER BY revenue DESC LIMIT 1;"),
        Task("mbc-t3", "Find customers who have placed an order containing a product from the 'Electronics' category, but who have NEVER ordered anything from the 'Clothing' category. Return customer name.", "", "SELECT DISTINCT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id JOIN products ON products.id = order_items.product_id WHERE products.category = 'Electronics' AND customers.id NOT IN (SELECT orders.customer_id FROM orders JOIN order_items ON order_items.order_id = orders.id JOIN products ON products.id = order_items.product_id WHERE products.category = 'Clothing');"),
        Task("mbc-t4", "For each category, find the product with the highest price. Return category, name, and price. Use a Window Function or CTE.", "", "WITH Ranked AS (SELECT category, name, price, ROW_NUMBER() OVER(PARTITION BY category ORDER BY price DESC) as rnk FROM products) SELECT category, name, price FROM Ranked WHERE rnk = 1;"),
        Task("mbc-t5", "Calculate the month-over-month growth in total revenue. Return the month (YYYY-MM), total_revenue, and the difference from the previous month's revenue (revenue_diff).", "", "WITH MonthlyRev AS (SELECT substr(orders.ordered_at, 1, 7) AS month, SUM(order_items.quantity * order_items.unit_price) AS revenue FROM orders JOIN order_items ON order_items.order_id = orders.id GROUP BY month) SELECT month, revenue, revenue - LAG(revenue) OVER(ORDER BY month) AS revenue_diff FROM MonthlyRev;"),
        Task("mbc-t6", "List pairs of customer names who have ordered the exact same product. Ensure no duplicate pairs (e.g., A-B is allowed, B-A is not). Return customer1, customer2, and product_name.", "", "SELECT DISTINCT c1.name AS customer1, c2.name AS customer2, p.name AS product_name FROM order_items o1 JOIN orders r1 ON r1.id = o1.order_id JOIN customers c1 ON c1.id = r1.customer_id JOIN order_items o2 ON o2.product_id = o1.product_id AND o2.order_id != o1.order_id JOIN orders r2 ON r2.id = o2.order_id JOIN customers c2 ON c2.id = r2.customer_id JOIN products p ON p.id = o1.product_id WHERE c1.id < c2.id;"),
        Task("mbc-t7", "Find the employee name who has the most 'resolved' support tickets. Return name and resolved_count.", "", "SELECT employees.name, COUNT(support_tickets.id) AS resolved_count FROM employees JOIN support_tickets ON support_tickets.employee_id = employees.id WHERE support_tickets.status = 'resolved' GROUP BY employees.id, employees.name ORDER BY resolved_count DESC LIMIT 1;"),
        Task("mbc-t8", "Identify orders that contain more than 3 distinct product categories. Return order_id and category_count.", "", "SELECT order_items.order_id, COUNT(DISTINCT products.category) AS category_count FROM order_items JOIN products ON products.id = order_items.product_id GROUP BY order_items.order_id HAVING COUNT(DISTINCT products.category) > 3;"),
        Task("mbc-t9", "Calculate a 2-order moving average of the total order value for each customer, ordered by order date. Return customer name, order_id, ordered_at, total_value, and moving_avg.", "", "WITH OrderValues AS (SELECT customers.name, orders.id, orders.ordered_at, SUM(order_items.quantity * order_items.unit_price) AS total_value FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.name, orders.id, orders.ordered_at) SELECT name, id, ordered_at, total_value, AVG(total_value) OVER(PARTITION BY name ORDER BY ordered_at ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) AS moving_avg FROM OrderValues;"),
        Task("mbc-t10", "Find the average number of days between a customer's first order and their second order. Return the 'avg_days_between_1st_and_2nd' rounded to 1 decimal place.", "", "WITH RankedOrders AS (SELECT customer_id, ordered_at, ROW_NUMBER() OVER(PARTITION BY customer_id ORDER BY ordered_at) AS rnk FROM orders), FirstTwo AS (SELECT customer_id, MAX(CASE WHEN rnk = 1 THEN ordered_at END) AS first_order, MAX(CASE WHEN rnk = 2 THEN ordered_at END) AS second_order FROM RankedOrders WHERE rnk <= 2 GROUP BY customer_id HAVING MAX(CASE WHEN rnk = 2 THEN ordered_at END) IS NOT NULL) SELECT ROUND(AVG(julianday(second_order) - julianday(first_order)), 1) AS avg_days_between_1st_and_2nd FROM FirstTwo;"),
        Task("mbc-t11", "Find products that have never been ordered at full price (where unit_price = price). Return product name.", "", "SELECT name FROM products WHERE id NOT IN (SELECT product_id FROM order_items JOIN products ON products.id = order_items.product_id WHERE order_items.unit_price = products.price) AND id IN (SELECT product_id FROM order_items);"),
        Task("mbc-t12", "For each product category, calculate the percentage of total company revenue it represents. Return category and pct_revenue rounded to 2 decimals.", "", "WITH CategoryRev AS (SELECT products.category, SUM(order_items.quantity * order_items.unit_price) AS rev FROM products JOIN order_items ON order_items.product_id = products.id GROUP BY products.category) SELECT category, ROUND(rev * 100.0 / SUM(rev) OVER(), 2) AS pct_revenue FROM CategoryRev;"),
        Task("mbc-t13", "Identify the customer who has ordered the highest total quantity of items from the 'Electronics' category. Return name and total_qty.", "", "SELECT customers.name, SUM(order_items.quantity) AS total_qty FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id JOIN products ON products.id = order_items.product_id WHERE products.category = 'Electronics' GROUP BY customers.id, customers.name ORDER BY total_qty DESC LIMIT 1;"),
        Task("mbc-t14", "List employees who manage someone, but do NOT have any unresolved support tickets assigned to them. Return employee name.", "", "SELECT DISTINCT m.name FROM employees m JOIN employees e ON e.manager_id = m.id WHERE m.id NOT IN (SELECT employee_id FROM support_tickets WHERE status != 'resolved' AND employee_id IS NOT NULL);"),
        Task("mbc-t15", "Find the month that had the highest number of newly registered customers (use their first order date as registration date). Return month (YYYY-MM) and new_customers.", "", "WITH FirstOrders AS (SELECT customer_id, MIN(ordered_at) AS first_date FROM orders GROUP BY customer_id) SELECT substr(first_date, 1, 7) AS month, COUNT(customer_id) AS new_customers FROM FirstOrders GROUP BY substr(first_date, 1, 7) ORDER BY new_customers DESC LIMIT 1;"),
        Task("mbc-t16", "Categorize customers into 'VIP' (spend > 1000), 'Regular' (spend between 500 and 1000), and 'Newbie' (spend < 500). Return name and category.", "", "WITH Spend AS (SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS total FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name) SELECT name, CASE WHEN total > 1000 THEN 'VIP' WHEN total >= 500 THEN 'Regular' ELSE 'Newbie' END AS category FROM Spend;"),
        Task("mbc-t17", "Find the shipping carrier that handles the highest volume of orders placed on weekends (Saturday/Sunday). Use strftime('%w'). Return carrier and weekend_orders.", "", "SELECT shipments.carrier, COUNT(orders.id) AS weekend_orders FROM shipments JOIN orders ON orders.id = shipments.order_id WHERE strftime('%w', orders.ordered_at) IN ('0', '6') GROUP BY shipments.carrier ORDER BY weekend_orders DESC LIMIT 1;"),
        Task("mbc-t18", "Identify orders where the total price of the order exceeds the average order total of all orders by more than 50%. Return order id and total_price.", "", "WITH OrderTotals AS (SELECT order_id, SUM(quantity * unit_price) AS total_price FROM order_items GROUP BY order_id) SELECT order_id, total_price FROM OrderTotals WHERE total_price > (SELECT AVG(total_price) * 1.5 FROM OrderTotals);"),
        Task("mbc-t19", "Find customers whose first-ever order included a heavily discounted item (where unit_price is less than 50% of the original product price). Return name.", "", "WITH RankedOrders AS (SELECT orders.customer_id, orders.id, ROW_NUMBER() OVER(PARTITION BY orders.customer_id ORDER BY orders.ordered_at ASC) as rnk FROM orders) SELECT DISTINCT customers.name FROM customers JOIN RankedOrders ON RankedOrders.customer_id = customers.id JOIN order_items ON order_items.order_id = RankedOrders.id JOIN products ON products.id = order_items.product_id WHERE RankedOrders.rnk = 1 AND order_items.unit_price < (products.price * 0.5);"),
        Task("mbc-t20", "Calculate the total inventory value of products that have NEVER been ordered. Return a single value 'dead_stock_value'.", "", "SELECT SUM(stock * price) AS dead_stock_value FROM products WHERE id NOT IN (SELECT product_id FROM order_items);"),
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
    "right-joins": "https://www.w3schools.com/sql/sql_join_right.asp",
    "full-joins": "https://www.w3schools.com/sql/sql_join_full.asp",
    "join-patterns": "https://www.w3schools.com/sql/sql_join.asp",
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
    "constraints-not-null-default": "https://www.w3schools.com/sql/sql_constraints.asp",
    "constraints-unique-check": "https://www.w3schools.com/sql/sql_unique.asp",
    "constraints-keys": "https://www.w3schools.com/sql/sql_primarykey.asp",
    "views": "https://www.w3schools.com/sql/sql_view.asp",
    "indexes": "https://www.w3schools.com/sql/sql_create_index.asp",
    "injection": "https://www.w3schools.com/sql/sql_injection.asp",
    "data-types": "https://www.w3schools.com/sql/sql_datatypes.asp",
    "insert-select": "https://www.w3schools.com/sql/sql_insert_into_select.asp",
    "union-intersect-except": "https://www.w3schools.com/sql/sql_union.asp",
    "advanced-review": "https://www.w3schools.com/sql/sql_any_all.asp",
    "interview-filters": "https://www.w3schools.com/sql/sql_between.asp",
    "string-functions": "https://www.sqlite.org/lang_corefunc.html",
    "date-analytics": "https://www.sqlite.org/lang_datefunc.html",
    "dates-advanced": "https://www.sqlite.org/lang_datefunc.html",
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
            "group": GROUP_BY_LESSON.get(lesson.id, "Other"),
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
        for row in conn.execute(f"SELECT * FROM {quote_identifier(table_name)} LIMIT 50")
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
GROUP_BY_LESSON = {
    "select-columns": "Basic Queries",
    "where-numeric": "Basic Queries",
    "where-text": "Basic Queries",
    "sorting-limits": "Basic Queries",
    "select-review": "Basic Queries",
    "basic-capstone": "Basic Queries",
    
    "inner-joins": "Joins",
    "outer-joins": "Joins",
    "right-joins": "Joins",
    "full-joins": "Joins",
    "self-joins": "Joins",
    "semi-anti-joins": "Joins",
    "join-patterns": "Joins",
    "joins-capstone": "Joins",
    
    "nulls": "Expressions & Types",
    "expressions": "Expressions & Types",
    "string-functions": "Expressions & Types",
    "date-analytics": "Expressions & Types",
    "dates-advanced": "Expressions & Types",
    "data-types": "Expressions & Types",
    "data-cleaning": "Expressions & Types",
    "expressions-capstone": "Expressions & Types",
    
    "aggregates": "Aggregations",
    "grouping": "Aggregations",
    "conditional-aggregation": "Aggregations",
    "aggregations-capstone": "Aggregations",
    
    "union-intersect-except": "Sets & Subqueries",
    "set-operations-advanced": "Sets & Subqueries",
    "advanced-review": "Sets & Subqueries",
    "sets-capstone": "Sets & Subqueries",
    
    "ctes": "Advanced Queries",
    "recursive-ctes": "Advanced Queries",
    "window-ranking": "Advanced Queries",
    "window-analytics": "Advanced Queries",
    "top-n-per-group": "Advanced Queries",
    "advanced-capstone": "Advanced Queries",
    
    "execution-order": "Theory & Execution",
    "indexes-query-plans": "Theory & Execution",
    "interview-filters": "Theory & Execution",
    
    "insert": "DDL & Admin",
    "update": "DDL & Admin",
    "delete": "DDL & Admin",
    "create-table": "DDL & Admin",
    "alter-table": "DDL & Admin",
    "drop-table": "DDL & Admin",
    "insert-select": "DDL & Admin",
    "constraints-not-null-default": "DDL & Admin",
    "constraints-unique-check": "DDL & Admin",
    "constraints-keys": "DDL & Admin",
    "views": "DDL & Admin",
    "indexes": "DDL & Admin",
    "injection": "DDL & Admin",
    "ddl-capstone": "DDL & Admin",
    
    "leetcode-patterns": "Interview Prep",
    "business-analytics": "Interview Prep",
    "final-interview-sets": "Interview Prep",
    "mixed-bag-capstone": "Interview Prep",
}
