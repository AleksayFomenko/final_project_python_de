CREATE SCHEMA IF NOT EXISTS dwh;
CREATE SCHEMA IF NOT EXISTS marts;

CREATE TABLE dwh.users (
    user_id BIGINT PRIMARY KEY,
    phone TEXT
);

CREATE TABLE dwh.stores (
    store_id BIGINT PRIMARY KEY,
    address TEXT
);

CREATE TABLE dwh.drivers (
    driver_id BIGINT PRIMARY KEY,
    phone TEXT
);

CREATE TABLE dwh.orders (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES dwh.users(user_id),
    store_id BIGINT REFERENCES dwh.stores(store_id),
    driver_id BIGINT REFERENCES dwh.drivers(driver_id),

    address TEXT,
    created_at TIMESTAMP,
    paid_at TIMESTAMP,
    delivery_started_at TIMESTAMP,
    delivered_at TIMESTAMP,
    canceled_at TIMESTAMP,

    payment_type TEXT,
    delivery_cost NUMERIC,
    order_discount NUMERIC,
    order_cancellation_reason TEXT
);

CREATE TABLE dwh.items (
    item_id BIGINT PRIMARY KEY,
    title TEXT,
    item_category TEXT
);

CREATE TABLE dwh.order_items (
    id SERIAL PRIMARY KEY,
    order_id BIGINT REFERENCES dwh.orders(order_id),
    item_id BIGINT REFERENCES dwh.items(item_id),
    quantity INT,
    price NUMERIC,
    canceled_quantity INT,
    item_replaced_id BIGINT,
    item_discount NUMERIC
);

--- tmp tables ---
CREATE TABLE IF NOT EXISTS dwh.users_tmp (
    user_id BIGINT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS dwh.stores_tmp (
    store_id BIGINT,
    address TEXT
);

CREATE TABLE IF NOT EXISTS dwh.drivers_tmp (
    driver_id BIGINT,
    phone TEXT
);

CREATE TABLE IF NOT EXISTS dwh.items_tmp (
    item_id BIGINT,
    title TEXT,
    item_category TEXT
);

CREATE TABLE IF NOT EXISTS dwh.orders_tmp (
    order_id BIGINT,
    user_id BIGINT,
    store_id BIGINT,
    driver_id BIGINT,
    address TEXT,
    created_at TIMESTAMP,
    paid_at TIMESTAMP,
    delivery_started_at TIMESTAMP,
    delivered_at TIMESTAMP,
    canceled_at TIMESTAMP,
    payment_type TEXT,
    delivery_cost NUMERIC,
    order_discount NUMERIC,
    order_cancellation_reason TEXT
);

CREATE TABLE IF NOT EXISTS dwh.order_items_tmp (
    order_id BIGINT,
    item_id BIGINT,
    quantity INT,
    price NUMERIC,
    canceled_quantity INT,
    item_replaced_id BIGINT,
    item_discount NUMERIC
);

--- marts tables (mirrors of dwh) ---

--- marts ---

-- Витрина заказов
CREATE TABLE IF NOT EXISTS marts.dm_orders_stats (
    dt                      DATE,
    year                    INT,
    month                   INT,
    store_id                BIGINT,
    store_address           TEXT,
    turnover                NUMERIC,
    revenue                 NUMERIC,
    profit                  NUMERIC,
    orders_count            BIGINT,
    delivered_count         BIGINT,
    canceled_count          BIGINT,
    canceled_after_delivery BIGINT,
    service_error_cancels   BIGINT,
    buyers_count            BIGINT,
    avg_check               NUMERIC,
    orders_per_buyer        NUMERIC,
    revenue_per_buyer       NUMERIC,
    courier_changes         BIGINT,
    active_couriers         BIGINT,
    PRIMARY KEY (dt, store_id)
);

-- Витрина товаров
CREATE TABLE IF NOT EXISTS marts.dm_items_stats (
    dt                  DATE,
    year                INT,
    month               INT,
    store_id            BIGINT,
    store_address       TEXT,
    item_id             BIGINT,
    item_title          TEXT,
    item_category       TEXT,
    item_turnover       NUMERIC,
    ordered_quantity    BIGINT,
    canceled_quantity   BIGINT,
    orders_with_item    BIGINT,
    orders_with_cancel  BIGINT,
    PRIMARY KEY (dt, store_id, item_id)
);

