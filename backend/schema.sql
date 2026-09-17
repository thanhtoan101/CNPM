-- Bootstrap for a NEW local development database. Review migrations separately for an existing database.
BEGIN;
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY, email TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('photographer','lab_owner','expert','moderator','admin'))
);
CREATE TABLE IF NOT EXISTS labs (
  id SERIAL PRIMARY KEY, owner_id INTEGER NOT NULL REFERENCES users(id),
  name VARCHAR(200) NOT NULL, address VARCHAR(500) NOT NULL, description TEXT NOT NULL DEFAULT '',
  rating NUMERIC(2,1) NOT NULL DEFAULT 0 CHECK (rating BETWEEN 0 AND 5)
);
CREATE TABLE IF NOT EXISTS services (
  id SERIAL PRIMARY KEY, lab_id INTEGER NOT NULL REFERENCES labs(id), name VARCHAR(200) NOT NULL,
  price NUMERIC(12,0) NOT NULL CHECK (price > 0), active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE IF NOT EXISTS orders (
  id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id),
  lab_id INTEGER NOT NULL REFERENCES labs(id), service_id INTEGER NOT NULL REFERENCES services(id),
  status TEXT NOT NULL DEFAULT 'pending', total_price NUMERIC(14,0) NOT NULL CHECK (total_price > 0),
  quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity BETWEEN 1 AND 100),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS orders_user_id_idx ON orders(user_id);
CREATE INDEX IF NOT EXISTS services_lab_id_idx ON services(lab_id);
CREATE TABLE IF NOT EXISTS courses (
  id SERIAL PRIMARY KEY, course_name VARCHAR(200) NOT NULL, description TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft','published','cancelled')),
  start_date TIMESTAMPTZ NOT NULL, end_date TIMESTAMPTZ NOT NULL CHECK (end_date >= start_date)
);
COMMIT;
