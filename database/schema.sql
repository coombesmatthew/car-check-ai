-- Car Check AI Database Schema

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Vehicle checks
CREATE TABLE IF NOT EXISTS vehicle_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    
    registration VARCHAR(20) NOT NULL,
    listing_url TEXT,
    listing_price INTEGER,
    
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    
    mot_data JSONB,
    market_data JSONB,
    analysis_result JSONB,
    
    status VARCHAR(50) DEFAULT 'pending',
    tier VARCHAR(20),
    price_paid INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_vehicle_checks_registration ON vehicle_checks(registration);
CREATE INDEX idx_vehicle_checks_status ON vehicle_checks(status);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    check_id UUID REFERENCES vehicle_checks(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'gbp',
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Market cache
CREATE TABLE IF NOT EXISTS market_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    make VARCHAR(100),
    model VARCHAR(100),
    year INTEGER,
    data JSONB NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP
);

CREATE INDEX idx_market_cache_lookup ON market_cache(make, model, year);
