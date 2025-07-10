-- Additional Supabase Schema for User Authentication
-- Run this in your Supabase SQL Editor AFTER running the main supabase-schema.sql

-- Create user profiles table to store additional user information
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    company TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on user profiles
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

-- User profiles policies
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = id);

-- Function to create user profile automatically
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.user_profiles (id, first_name, last_name, full_name, company)
    VALUES (
        new.id,
        new.raw_user_meta_data->>'first_name',
        new.raw_user_meta_data->>'last_name',
        new.raw_user_meta_data->>'full_name',
        new.raw_user_meta_data->>'company'
    );
    RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to create profile on user registration
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- Update existing RLS policies to require authentication
-- Drop existing policies
DROP POLICY IF EXISTS "Enable read access for all users" ON suppliers;
DROP POLICY IF EXISTS "Enable read access for all users" ON products;
DROP POLICY IF EXISTS "Enable read access for all users" ON forecast_data;
DROP POLICY IF EXISTS "Enable read access for all users" ON alerts;
DROP POLICY IF EXISTS "Enable read access for all users" ON inventory_transactions;

-- Create authenticated user policies for suppliers
CREATE POLICY "Authenticated users can view suppliers" ON suppliers
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can modify suppliers" ON suppliers
    FOR ALL TO authenticated USING (true);

-- Create authenticated user policies for products
CREATE POLICY "Authenticated users can view products" ON products
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can modify products" ON products
    FOR ALL TO authenticated USING (true);

-- Create authenticated user policies for forecast_data
CREATE POLICY "Authenticated users can view forecasts" ON forecast_data
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can modify forecasts" ON forecast_data
    FOR ALL TO authenticated USING (true);

-- Create authenticated user policies for alerts
CREATE POLICY "Authenticated users can view alerts" ON alerts
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can modify alerts" ON alerts
    FOR ALL TO authenticated USING (true);

-- Create authenticated user policies for inventory_transactions
CREATE POLICY "Authenticated users can view transactions" ON inventory_transactions
    FOR SELECT TO authenticated USING (true);

CREATE POLICY "Authenticated users can modify transactions" ON inventory_transactions
    FOR ALL TO authenticated USING (true);

-- Update permissions to remove anonymous access
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon;
GRANT USAGE ON SCHEMA public TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO authenticated;

-- Create a function to get current user profile
CREATE OR REPLACE FUNCTION get_current_user_profile()
RETURNS TABLE (
    id UUID,
    email TEXT,
    first_name TEXT,
    last_name TEXT,
    full_name TEXT,
    company TEXT,
    avatar_url TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.id,
        u.email,
        p.first_name,
        p.last_name,
        p.full_name,
        p.company,
        p.avatar_url
    FROM auth.users u
    LEFT JOIN user_profiles p ON u.id = p.id
    WHERE u.id = auth.uid();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permission on the function
GRANT EXECUTE ON FUNCTION get_current_user_profile() TO authenticated; 