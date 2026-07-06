# Database Schema Reference

This document summarizes the retail database schema used by the project.

## Tables

### stores
| Column | Type | Notes |
| --- | --- | --- |
| store_id | VARCHAR(20) | Primary key |
| store_name | VARCHAR(100) | Not null |
| region | VARCHAR(50) | Optional |
| city | VARCHAR(50) | Optional |
| store_type | VARCHAR(50) | Optional |

### products
| Column | Type | Notes |
| --- | --- | --- |
| product_id | VARCHAR(20) | Primary key |
| product_name | VARCHAR(100) | Not null |
| category | VARCHAR(50) | Optional |
| sub_category | VARCHAR(50) | Optional |
| base_price | DECIMAL(12,2) | Optional |

### customers
| Column | Type | Notes |
| --- | --- | --- |
| customer_id | VARCHAR(20) | Primary key |
| customer_segment | VARCHAR(50) | Optional |
| signup_date | DATE | Optional |
| preferred_channel | VARCHAR(50) | Optional |
| city | VARCHAR(50) | Optional |

### sales_transactions
| Column | Type | Notes |
| --- | --- | --- |
| order_id | VARCHAR(20) | Primary key |
| order_date | DATE | Optional |
| store_id | VARCHAR(20) | Foreign key to stores.store_id |
| product_id | VARCHAR(20) | Foreign key to products.product_id |
| customer_id | VARCHAR(20) | Foreign key to customers.customer_id |
| sales_channel | VARCHAR(50) | Optional |
| units_sold | INT | Optional |
| unit_price | DECIMAL(12,2) | Optional |
| discount_pct | DECIMAL(5,2) | Optional |
| payment_status | VARCHAR(50) | Optional |
| delivery_status | VARCHAR(50) | Optional |

### returns
| Column | Type | Notes |
| --- | --- | --- |
| return_id | VARCHAR(20) | Primary key |
| order_id | VARCHAR(20) | Foreign key to sales_transactions.order_id |
| return_date | DATE | Optional |
| return_reason | VARCHAR(255) | Optional |

## Relationships
- sales_transactions.store_id -> stores.store_id
- sales_transactions.product_id -> products.product_id
- sales_transactions.customer_id -> customers.customer_id
- returns.order_id -> sales_transactions.order_id
