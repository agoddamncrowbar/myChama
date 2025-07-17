-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    id_scan_url VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chamas table
CREATE TABLE chamas (
    chama_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    guidelines TEXT,
    monthly_contribution DECIMAL(10,2) NOT NULL
);

-- Chama members (many-to-many relationship)
CREATE TABLE chama_members (
    member_id SERIAL PRIMARY KEY,
    chama_id INTEGER REFERENCES chamas(chama_id),
    user_id INTEGER REFERENCES users(user_id),
    role VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'treasurer', 'secretary', 'member')),
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chama_id, user_id)
);

-- Contributions/payments
CREATE TABLE contributions (
    contribution_id SERIAL PRIMARY KEY,
    chama_id INTEGER REFERENCES chamas(chama_id),
    member_id INTEGER REFERENCES chama_members(member_id),
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mpesa_code VARCHAR(50) UNIQUE,
    verified BOOLEAN DEFAULT FALSE
);

-- Loans
CREATE TABLE loans (
    loan_id SERIAL PRIMARY KEY,
    chama_id INTEGER REFERENCES chamas(chama_id),
    member_id INTEGER REFERENCES chama_members(member_id),
    amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) DEFAULT 0.0,
    disbursement_date TIMESTAMP,
    due_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'paid', 'defaulted')),
    purpose TEXT
);

-- Loan payments
CREATE TABLE loan_payments (
    payment_id SERIAL PRIMARY KEY,
    loan_id INTEGER REFERENCES loans(loan_id),
    amount DECIMAL(10,2) NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mpesa_code VARCHAR(50) UNIQUE
);

-- Meetings
CREATE TABLE meetings (
    meeting_id SERIAL PRIMARY KEY,
    chama_id INTEGER REFERENCES chamas(chama_id),
    meeting_date TIMESTAMP NOT NULL,
    location VARCHAR(255),
    agenda TEXT,
    minutes TEXT
);