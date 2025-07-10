-- Temporary Fix for Backend API Access
-- Run this in your Supabase SQL Editor to allow backend API to work
-- This grants minimal read access to anonymous users for the backend API

-- Grant read-only access to anonymous users for the backend API
GRANT SELECT ON suppliers TO anon;
GRANT SELECT ON products TO anon;
GRANT SELECT ON forecast_data TO anon;
GRANT SELECT ON alerts TO anon;
GRANT SELECT ON inventory_transactions TO anon;

-- Allow the backend to insert/update alerts (for notifications)
GRANT INSERT, UPDATE ON alerts TO anon;

-- Allow the backend to insert forecast data (for forecasting pipeline)
GRANT INSERT, UPDATE ON forecast_data TO anon;

-- Allow the backend to insert inventory transactions (for stock updates)
GRANT INSERT ON inventory_transactions TO anon;

-- Update products current_stock (for inventory management)
GRANT UPDATE (current_stock) ON products TO anon;

-- Note: This maintains authentication for the frontend (RLS still applies)
-- while allowing the backend API to function properly
-- The backend should still use the service role key for production 