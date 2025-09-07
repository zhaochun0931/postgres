-- ==============================================
-- PostgreSQL Index Demo
-- ==============================================

-- 1. Drop old table if exists
DROP TABLE IF EXISTS users;

-- 2. Create demo table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- 3. Insert 1 million rows
INSERT INTO users (name, email, created_at)
SELECT
    'User' || g,
    'user' || g || '@example.com',
    now() - (random() * interval '365 days')
FROM generate_series(1, 1000000) g;

-- Force analyze so planner knows stats
ANALYZE users;

-- 4. Query WITHOUT index
\echo '==== Query without index ===='
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user500000@example.com';

-- 5. Create index on email
CREATE INDEX idx_users_email ON users(email);

-- 6. Query WITH index
\echo '==== Query with index ===='
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user500000@example.com';
