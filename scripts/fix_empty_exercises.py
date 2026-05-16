"""Fix exercises with 0 results or schema errors against the seed data.

Approach:
- For schema errors (missing columns/tables): rewrite the solution to use existing columns
- For data mismatches (empty results): adjust the WHERE values to match actual seed data
"""
import re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# Map of task_id -> (new_prompt, new_solution)
# Based on actual schema and seed data analysis
FIXES = {
    # ======= SCHEMA FIXES (missing columns) =======

    # bc-t2: no 'email' column on customers
    "bc-t2": (
        "Find the cities of customers who live in 'Canada'.",
        "SELECT city FROM customers WHERE country = 'Canada';",
    ),
    # bc-t19: no 'email' on customers
    "bc-t19": (
        "Identify customers whose city name ends with 'ore'. Return name and city.",
        "SELECT name, city FROM customers WHERE city LIKE '%ore';",
    ),
    # l29-t9: support_tickets has no employee_id — it has customer_id, order_id
    "l29-t9": (
        "Right Semi Join using IN: Find customer IDs that have submitted at least one support ticket. Use IN. Sort by id.",
        "SELECT id FROM customers WHERE id IN (SELECT customer_id FROM support_tickets) ORDER BY id;",
    ),
    # l29-t11: support_tickets has no employee_id
    "l29-t11": (
        "Left Anti Join: Find customers who have never submitted a support ticket. Use NOT EXISTS. Sort by name.",
        "SELECT name FROM customers WHERE NOT EXISTS (SELECT 1 FROM support_tickets WHERE support_tickets.customer_id = customers.id) ORDER BY name;",
    ),
    # jc-t11: support_tickets has no 'issue' column
    "jc-t11": (
        "List any support tickets that are unassigned to an order or are still open. Return ticket id and priority.",
        "SELECT id, priority FROM support_tickets WHERE order_id IS NULL OR status = 'open';",
    ),
    # jc-t16: customers have no 'email'
    "jc-t16": (
        "Determine which customers have submitted support tickets. Return the customer name.",
        "SELECT DISTINCT customers.name FROM customers JOIN support_tickets ON support_tickets.customer_id = customers.id;",
    ),
    # ec-t1: no 'email' on customers
    "ec-t1": (
        "Extract the country code (first 2 characters) from every customer's country. Return name and 'code'.",
        "SELECT name, SUBSTR(country, 1, 2) AS code FROM customers;",
    ),
    # ac-t3: support_tickets has no employee_id
    "ac-t3": (
        "Count the number of support tickets per priority level. Return priority and ticket_count, sorted by ticket_count descending.",
        "SELECT priority, COUNT(*) AS ticket_count FROM support_tickets GROUP BY priority ORDER BY ticket_count DESC;",
    ),
    # ac-t18: support_tickets has no employee_id
    "ac-t18": (
        "For each customer, calculate the total number of support tickets they have opened. Return customer_id and ticket_count, sorted by ticket_count descending.",
        "SELECT customer_id, COUNT(*) AS ticket_count FROM support_tickets GROUP BY customer_id ORDER BY ticket_count DESC;",
    ),
    # sc-t12: no 'email' on either table
    "sc-t12": (
        "List the names of customers that perfectly match the names of employees. Use INTERSECT.",
        "SELECT name FROM employees INTERSECT SELECT name FROM customers;",
    ),
    # sc-t17: support_tickets has no employee_id
    "sc-t17": (
        "Find all support tickets assigned to orders placed by customers from 'India'. Use an IN subquery.",
        "SELECT id FROM support_tickets WHERE order_id IN (SELECT id FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE country = 'India'));",
    ),
    # sc-t18: no 'email' on tables
    "sc-t18": (
        "Create a single list containing all unique customer names AND all unique employee names. Use UNION.",
        "SELECT name FROM customers UNION SELECT name FROM employees;",
    ),
    # adc-t17: LEAD() can't be used in WHERE clause in SQLite
    "adc-t17": (
        "Identify gaps in order IDs (if any exist between MIN and MAX). Use a CTE with LEAD to find where the next ID is not ID+1. Return id and next_id.",
        "WITH OrderGaps AS (SELECT id, LEAD(id) OVER(ORDER BY id) AS next_id FROM orders) SELECT id, next_id FROM OrderGaps WHERE next_id IS NOT NULL AND next_id != id + 1;",
    ),
    # l47-t3: injection uses 'email' which doesn't exist
    "l47-t3": (
        "Hacker Mode: Show what happens if someone types `' OR '1'='1` into a name search field. The vulnerable query is: SELECT * FROM customers WHERE name = '[INPUT]'.",
        "SELECT * FROM customers WHERE name = '' OR '1'='1';",
    ),
    # dc-t17: no 'admins' table
    "dc-t17": (
        "Hacker Mode: Bypass an authentication query. Write the resulting query if you inject `' OR 1=1 --` into the name field of `SELECT * FROM customers WHERE name = '[INPUT]'`.",
        "SELECT * FROM customers WHERE name = '' OR 1=1 --;",
    ),
    # mbc-t7: support_tickets has no employee_id
    "mbc-t7": (
        "Find the customer who has opened the most support tickets. Return name and ticket_count.",
        "SELECT customers.name, COUNT(support_tickets.id) AS ticket_count FROM customers JOIN support_tickets ON support_tickets.customer_id = customers.id GROUP BY customers.id, customers.name ORDER BY ticket_count DESC LIMIT 1;",
    ),
    # mbc-t14: support_tickets has no employee_id
    "mbc-t14": (
        "List employees who are managers but whose managed employees have never had a customer submit a support ticket on one of their orders. Return employee name.",
        "SELECT DISTINCT m.name FROM employees m JOIN employees e ON e.manager_id = m.id WHERE m.id NOT IN (SELECT e2.manager_id FROM employees e2 WHERE e2.manager_id IS NOT NULL);",
    ),

    # ======= DATA FIXES (empty results) =======

    # bc-t3: no product costs 19.99 -> use 89.99 which exists
    "bc-t3": (
        "List all products that cost exactly 89.99.",
        "SELECT * FROM products WHERE price = 89.99;",
    ),
    # bc-t4: no 'pending' orders -> use 'processing'
    "bc-t4": (
        "Identify orders that have a status of 'processing'. Return the order IDs.",
        "SELECT id FROM orders WHERE status = 'processing';",
    ),
    # bc-t7: no customer name starts with 'J' -> use 'M'
    "bc-t7": (
        "Find all customers whose name starts with the letter 'M'. Return their names.",
        "SELECT name FROM customers WHERE name LIKE 'M%';",
    ),
    # bc-t12: no 'Electronics' over 500 -> use over 100
    "bc-t12": (
        "List all products that belong to the 'Electronics' category and cost more than 100.",
        "SELECT * FROM products WHERE category = 'Electronics' AND price > 100;",
    ),
    # bc-t14: no product contains 'Pro' -> use 'Noise'
    "bc-t14": (
        "Identify products whose name contains the word 'Noise'. Return name.",
        "SELECT name FROM products WHERE name LIKE '%Noise%';",
    ),
    # bc-t18: no stock between 1-9 -> use between 1-20
    "bc-t18": (
        "Find products where the stock is dangerously low (less than 20) but not completely out. Return name and stock.",
        "SELECT name, stock FROM products WHERE stock > 0 AND stock < 20;",
    ),
    # l7-t5: all customers have orders -> remove customer 8 from orders or adjust
    # Actually checking: all 8 customers (1-8) appear in orders. So this is validly empty.
    # We need to rephrase: "Find customers who have never had a SHIPPED order"
    "l7-t5": (
        "Find customers who have never had a cancelled order. Show name, sorted by name.",
        "SELECT customers.name FROM customers LEFT JOIN orders ON orders.customer_id = customers.id AND orders.status = 'cancelled' WHERE orders.id IS NULL ORDER BY customers.name;",
    ),
    # l9f-t2: FULL JOIN - no orphaned data exists
    "l9f-t2": (
        "Show all customers and all orders using a FULL JOIN. Include unmatched rows from both sides. Show customer name and order id, sorted by order id.",
        "SELECT customers.name, orders.id FROM customers FULL JOIN orders ON orders.customer_id = customers.id ORDER BY orders.id;",
    ),
    # l30-t5: no customers with 2 orders on same date... actually customer 1 has orders on 2024-01-05 and 2024-01-09, customer 3 has 2024-01-11 and 2024-03-09. No same date pairs.
    # Let's change to: same channel
    "l30-t5": (
        "Find customers who placed two distinct orders through the same channel without duplicate mirrored pairs. Show customer_id, channel, order_a_id, and order_b_id. Sort by customer_id then order_a_id.",
        "SELECT a.customer_id, a.channel, a.id AS order_a_id, b.id AS order_b_id FROM orders a JOIN orders b ON a.customer_id = b.customer_id AND a.channel = b.channel AND a.id < b.id ORDER BY a.customer_id, order_a_id;",
    ),
    # l29-t2: all customers have orders -> rephrase
    "l29-t2": (
        "Find customers who have never had a cancelled order using NOT EXISTS. Show name, sorted by name.",
        "SELECT name FROM customers WHERE NOT EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id AND orders.status = 'cancelled') ORDER BY name;",
    ),
    # l29-t13: no 'MacBook Pro' product -> use 'Mechanical Keyboard'
    "l29-t13": (
        "Left Semi Join vs DISTINCT JOIN: Find customer names who have ordered 'Mechanical Keyboard'. Use IN with a chained subquery (no JOINs in the outer query). Sort by name.",
        "SELECT name FROM customers WHERE id IN (SELECT customer_id FROM orders WHERE id IN (SELECT order_id FROM order_items WHERE product_id = (SELECT id FROM products WHERE name = 'Mechanical Keyboard'))) ORDER BY name;",
    ),
    # l29-t15: no customer with more than 2 orders -> customer 1 has 2, customer 3 has 2. Use >= 2
    "l29-t15": (
        "Left Semi Join with aggregation: Find customer names who have placed 2 or more orders. Use EXISTS with a correlated subquery that uses GROUP BY and HAVING. Sort by name.",
        "SELECT name FROM customers WHERE EXISTS (SELECT 1 FROM orders WHERE orders.customer_id = customers.id GROUP BY orders.customer_id HAVING COUNT(*) >= 2) ORDER BY name;",
    ),
    # l10j-t5: FULL JOIN orphan data - no orphans exist
    "l10j-t5": (
        "Scenario: 'Build a complete picture: Show every customer alongside any orders they may have, even if a customer never ordered.' Return customer name and order id, sorted by customer name then order id.",
        "SELECT customers.name, orders.id FROM customers LEFT JOIN orders ON orders.customer_id = customers.id ORDER BY customers.name, orders.id;",
    ),
    # jc-t1: all customers have orders -> use 'shipped' filter
    "jc-t1": (
        "Identify customers who have placed an order but none of their orders have been delivered yet. Return their name.",
        "SELECT DISTINCT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id WHERE customers.id NOT IN (SELECT customer_id FROM orders WHERE status = 'delivered');",
    ),
    # jc-t14: no 'FedEx' carrier -> use 'ShipFast'
    "jc-t14": (
        "Find customers whose orders were shipped via 'ShipFast'. Return unique customer names.",
        "SELECT DISTINCT customers.name FROM customers JOIN orders ON orders.customer_id = customers.id JOIN shipments ON shipments.order_id = orders.id WHERE shipments.carrier = 'ShipFast';",
    ),
    # jc-t17: no 'MacBook Pro' -> use 'USB-C Hub'
    "jc-t17": (
        "List all order IDs that contain the product 'USB-C Hub'.",
        "SELECT DISTINCT order_items.order_id FROM order_items JOIN products ON products.id = order_items.product_id WHERE products.name = 'USB-C Hub';",
    ),
    # ec-t6: no product contains 'Pro' -> use 'Desk'
    "ec-t6": (
        "Replace the word 'Desk' with 'Desktop' in any product name that contains it. Return original name and 'new_name'.",
        "SELECT name, REPLACE(name, 'Desk', 'Desktop') AS new_name FROM products WHERE name LIKE '%Desk%';",
    ),
    # ac-t11: no 'FedEx' carrier -> use 'ShipFast'
    "ac-t11": (
        "Determine the average time to ship (shipped_at - ordered_at in days) for ShipFast shipments. Return avg_ship_days rounded to 1 decimal.",
        "SELECT ROUND(AVG(julianday(shipments.shipped_at) - julianday(orders.ordered_at)), 1) AS avg_ship_days FROM shipments JOIN orders ON orders.id = shipments.order_id WHERE shipments.carrier = 'ShipFast';",
    ),
    # ac-t17: no category avg > 500 -> use > 50
    "ac-t17": (
        "Identify product categories where the average price exceeds 50. Return category and avg_price.",
        "SELECT category, AVG(price) AS avg_price FROM products GROUP BY category HAVING AVG(price) > 50;",
    ),
    # ac-t20: no customer spend > 1000 -> use > 100
    "ac-t20": (
        "Find customers whose total lifetime spend exceeds 100. Return customer name and total_spend.",
        "SELECT customers.name, SUM(order_items.quantity * order_items.unit_price) AS total_spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name HAVING SUM(order_items.quantity * order_items.unit_price) > 100;",
    ),
    # sc-t9: no customer named 'Alice' -> use 'Asha Rao'
    "sc-t9": (
        "Find customers who reside in the same country as the customer named 'Asha Rao'. Exclude Asha Rao herself.",
        "SELECT name FROM customers WHERE country = (SELECT country FROM customers WHERE name = 'Asha Rao') AND name != 'Asha Rao';",
    ),
    # sc-t11: no product priced over 1000 -> use over 80
    "sc-t11": (
        "Find product categories that contain a product priced over 80. Use a subquery.",
        "SELECT DISTINCT category FROM products WHERE category IN (SELECT category FROM products WHERE price > 80);",
    ),
    # adc-t12: no customer spend > 500 -> use > 100
    "adc-t12": (
        "Use a CTE to calculate the total lifetime spend per customer, then select customers who spent over 100.",
        "WITH Spend AS (SELECT customers.id, customers.name, SUM(order_items.quantity * order_items.unit_price) AS total_spend FROM customers JOIN orders ON orders.customer_id = customers.id JOIN order_items ON order_items.order_id = orders.id GROUP BY customers.id, customers.name) SELECT name, total_spend FROM Spend WHERE total_spend > 100;",
    ),
    # mbc-t8: no order with > 3 distinct categories -> use > 1
    "mbc-t8": (
        "Identify orders that contain more than 1 distinct product category. Return order_id and category_count.",
        "SELECT order_items.order_id, COUNT(DISTINCT products.category) AS category_count FROM order_items JOIN products ON products.id = order_items.product_id GROUP BY order_items.order_id HAVING COUNT(DISTINCT products.category) > 1;",
    ),
    # mbc-t19: no customer with first order having < 50% discount item -> adjust threshold
    "mbc-t19": (
        "Find customers whose first-ever order included an item where the unit price differs from the original product price. Return name.",
        "WITH RankedOrders AS (SELECT orders.customer_id, orders.id, ROW_NUMBER() OVER(PARTITION BY orders.customer_id ORDER BY orders.ordered_at ASC) as rnk FROM orders) SELECT DISTINCT customers.name FROM customers JOIN RankedOrders ON RankedOrders.customer_id = customers.id JOIN order_items ON order_items.order_id = RankedOrders.id JOIN products ON products.id = order_items.product_id WHERE RankedOrders.rnk = 1 AND order_items.unit_price != products.price;",
    ),
}

def apply_fixes():
    with open("app/sql_practice.py", "r") as f:
        content = f.read()

    count = 0
    for task_id, (new_prompt, new_solution) in FIXES.items():
        # Find the Task with this ID and replace prompt + solution
        # Pattern: Task("task_id", "old_prompt", "old_starter", "old_solution"
        pattern = rf'(Task\("{re.escape(task_id)}",\s*)"((?:[^"\\]|\\.)*)(",\s*"(?:[^"\\]|\\.)*",\s*)"((?:[^"\\]|\\.)*)"'
        match = re.search(pattern, content)
        if match:
            old_full = match.group(0)
            new_full = f'{match.group(1)}"{new_prompt}"{match.group(3)}"{new_solution}"'
            content = content.replace(old_full, new_full, 1)
            count += 1
            print(f"  ✓ Fixed {task_id}")
        else:
            print(f"  ✗ Could not find {task_id}")

    with open("app/sql_practice.py", "w") as f:
        f.write(content)

    print(f"\nApplied {count}/{len(FIXES)} fixes.")

if __name__ == "__main__":
    apply_fixes()
