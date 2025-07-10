-- Chronos AI Supply Chain Database Schema
-- Run this in your Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Suppliers table
CREATE TABLE suppliers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    lead_time_days INTEGER DEFAULT 7,
    reliability_score DECIMAL(3,2) DEFAULT 0.95 CHECK (reliability_score >= 0 AND reliability_score <= 1),
    risk_level TEXT DEFAULT 'medium' CHECK (risk_level IN ('low', 'medium', 'high')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Products table
CREATE TABLE products (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(100) NOT NULL,
    current_stock INTEGER DEFAULT 0 CHECK (current_stock >= 0),
    reorder_point INTEGER DEFAULT 10 CHECK (reorder_point >= 0),
    unit_cost DECIMAL(10,2) DEFAULT 0 CHECK (unit_cost >= 0),
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Forecast data table
CREATE TABLE forecast_data (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    predicted_demand DECIMAL(10,2) NOT NULL CHECK (predicted_demand >= 0),
    confidence_interval_lower DECIMAL(10,2) NOT NULL CHECK (confidence_interval_lower >= 0),
    confidence_interval_upper DECIMAL(10,2) NOT NULL CHECK (confidence_interval_upper >= confidence_interval_lower),
    actual_demand DECIMAL(10,2) CHECK (actual_demand >= 0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, date)
);

-- Alerts table
CREATE TABLE alerts (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('stock_low', 'demand_spike', 'supplier_risk', 'forecast_anomaly')),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    product_id UUID REFERENCES products(id) ON DELETE SET NULL,
    supplier_id UUID REFERENCES suppliers(id) ON DELETE SET NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

-- Inventory transactions table
CREATE TABLE inventory_transactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('inbound', 'outbound', 'adjustment')),
    quantity INTEGER NOT NULL,
    unit_cost DECIMAL(10,2),
    reference_number VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_products_supplier_id ON products(supplier_id);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_current_stock ON products(current_stock);
CREATE INDEX idx_forecast_data_product_date ON forecast_data(product_id, date);
CREATE INDEX idx_alerts_severity_resolved ON alerts(severity, is_resolved);
CREATE INDEX idx_alerts_created_at ON alerts(created_at DESC);
CREATE INDEX idx_inventory_transactions_product_id ON inventory_transactions(product_id);
CREATE INDEX idx_inventory_transactions_created_at ON inventory_transactions(created_at DESC);

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at for products
CREATE TRIGGER update_products_updated_at 
    BEFORE UPDATE ON products
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO suppliers (name, contact_email, lead_time_days, reliability_score, risk_level) VALUES
('TechCorp Industries', 'orders@techcorp.com', 5, 0.98, 'low'),
('Global Electronics Ltd', 'supply@globalelec.com', 10, 0.92, 'medium'),
('FastTrack Components', 'sales@fasttrack.com', 3, 0.85, 'high'),
('Reliable Supplies Co', 'contact@reliable.com', 7, 0.96, 'low');

INSERT INTO products (name, sku, category, current_stock, reorder_point, unit_cost, supplier_id) VALUES
('Wireless Headphones Pro', 'WHP-001', 'Electronics', 45, 50, 79.99, (SELECT id FROM suppliers WHERE name = 'TechCorp Industries' LIMIT 1)),
('USB-C Cable 2m', 'USC-002', 'Accessories', 120, 100, 12.99, (SELECT id FROM suppliers WHERE name = 'FastTrack Components' LIMIT 1)),
('Bluetooth Speaker', 'BTS-003', 'Electronics', 75, 40, 45.99, (SELECT id FROM suppliers WHERE name = 'Global Electronics Ltd' LIMIT 1)),
('Phone Case Premium', 'PCP-004', 'Accessories', 200, 150, 24.99, (SELECT id FROM suppliers WHERE name = 'Reliable Supplies Co' LIMIT 1)),
('Laptop Stand Aluminum', 'LSA-005', 'Accessories', 35, 25, 34.99, (SELECT id FROM suppliers WHERE name = 'TechCorp Industries' LIMIT 1));

-- Insert sample forecast data (next 30 days)
INSERT INTO forecast_data (product_id, date, predicted_demand, confidence_interval_lower, confidence_interval_upper)
SELECT 
    p.id,
    (CURRENT_DATE + generate_series(1, 30))::date,
    ROUND((RANDOM() * 20 + 10)::numeric, 2) as predicted_demand,
    ROUND((RANDOM() * 10 + 5)::numeric, 2) as confidence_interval_lower,
    ROUND((RANDOM() * 30 + 15)::numeric, 2) as confidence_interval_upper
FROM products p;

-- Insert sample alerts
INSERT INTO alerts (type, severity, title, description, product_id) VALUES
('stock_low', 'high', 'Low Stock Alert', 'Wireless Headphones Pro stock is below reorder point', (SELECT id FROM products WHERE sku = 'WHP-001')),
('demand_spike', 'medium', 'Demand Increase Detected', 'Bluetooth Speaker showing 25% increase in demand', (SELECT id FROM products WHERE sku = 'BTS-003')),
('forecast_anomaly', 'low', 'Forecast Accuracy Drop', 'Model accuracy decreased for USB-C Cable 2m', (SELECT id FROM products WHERE sku = 'USC-002'));

-- Insert sample inventory transactions
INSERT INTO inventory_transactions (product_id, type, quantity, reference_number, notes)
SELECT 
    p.id,
    CASE WHEN random() < 0.6 THEN 'outbound' ELSE 'inbound' END,
    FLOOR(random() * 50 + 1)::integer,
    'TXN-' || LPAD((random() * 9999)::text, 4, '0'),
    'Sample transaction data'
FROM products p, generate_series(1, 3) s;

-- Enable Row Level Security (RLS) for production use
ALTER TABLE suppliers ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE forecast_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE inventory_transactions ENABLE ROW LEVEL SECURITY;

-- Create policies (modify these based on your authentication requirements)
CREATE POLICY "Enable read access for all users" ON suppliers FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON products FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON forecast_data FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON alerts FOR SELECT USING (true);
CREATE POLICY "Enable read access for all users" ON inventory_transactions FOR SELECT USING (true);

-- Grant necessary permissions (adjust based on your needs)
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated; 