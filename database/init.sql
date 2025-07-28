-- Create database
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'AgentSystem')
BEGIN
    CREATE DATABASE AgentSystem;
END;
GO

USE AgentSystem;
GO

-- Create login and user
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'usrmon')
BEGIN
    CREATE LOGIN usrmon WITH PASSWORD = 'MonAplic01@';
END;
GO

IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'usrmon')
BEGIN
    CREATE USER usrmon FOR LOGIN usrmon;
    ALTER ROLE db_owner ADD MEMBER usrmon;
END;
GO

-- Users table
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) UNIQUE NOT NULL,
    email NVARCHAR(100) UNIQUE NOT NULL,
    hashed_password NVARCHAR(255) NOT NULL,
    full_name NVARCHAR(100),
    role NVARCHAR(20) DEFAULT 'User' CHECK (role IN ('Admin', 'User', 'Viewer')),
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- API Keys table
CREATE TABLE api_keys (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE,
    key_name NVARCHAR(100) NOT NULL,
    api_key NVARCHAR(255) UNIQUE NOT NULL,
    is_active BIT DEFAULT 1,
    rate_limit_per_minute INT DEFAULT 60,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    last_used_at DATETIME2
);
GO

-- System configuration table
CREATE TABLE system_config (
    id INT IDENTITY(1,1) PRIMARY KEY,
    config_key NVARCHAR(100) UNIQUE NOT NULL,
    config_value NVARCHAR(MAX),
    description NVARCHAR(500),
    is_encrypted BIT DEFAULT 0,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Encrypted credentials table
CREATE TABLE encrypted_credentials (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE,
    credential_name NVARCHAR(100) NOT NULL,
    encrypted_data NVARCHAR(MAX) NOT NULL,
    credential_type NVARCHAR(50),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Prompt templates table
CREATE TABLE prompt_templates (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    template_content NVARCHAR(MAX) NOT NULL,
    description NVARCHAR(500),
    variables NVARCHAR(MAX), -- JSON array of variable names
    version INT DEFAULT 1,
    is_active BIT DEFAULT 1,
    created_by INT FOREIGN KEY REFERENCES users(id),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Tools table
CREATE TABLE tools (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) UNIQUE NOT NULL,
    description NVARCHAR(500),
    endpoint_template NVARCHAR(MAX) NOT NULL,
    method_allowed NVARCHAR(100) DEFAULT 'GET,POST,PUT,DELETE',
    default_headers NVARCHAR(MAX), -- JSON
    requires_auth BIT DEFAULT 0,
    cost_per_request DECIMAL(10,6) DEFAULT 0.0,
    timeout_seconds INT DEFAULT 30,
    is_active BIT DEFAULT 1,
    created_by INT FOREIGN KEY REFERENCES users(id),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Agents table
CREATE TABLE agents (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(500),
    system_prompt NVARCHAR(MAX),
    personality NVARCHAR(MAX),
    model_name NVARCHAR(50) DEFAULT 'gpt-3.5-turbo',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INT DEFAULT 1000,
    top_p DECIMAL(3,2) DEFAULT 1.0,
    frequency_penalty DECIMAL(3,2) DEFAULT 0.0,
    presence_penalty DECIMAL(3,2) DEFAULT 0.0,
    rate_limit_per_minute INT DEFAULT 10,
    is_active BIT DEFAULT 1,
    created_by INT FOREIGN KEY REFERENCES users(id),
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    updated_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Agent-Tools relationship table
CREATE TABLE agent_tools (
    id INT IDENTITY(1,1) PRIMARY KEY,
    agent_id INT FOREIGN KEY REFERENCES agents(id) ON DELETE CASCADE,
    tool_id INT FOREIGN KEY REFERENCES tools(id) ON DELETE CASCADE,
    configuration NVARCHAR(MAX), -- JSON configuration for this specific agent-tool combination
    is_active BIT DEFAULT 1,
    created_at DATETIME2 DEFAULT GETUTCDATE(),
    UNIQUE(agent_id, tool_id)
);
GO

-- Executions table
CREATE TABLE executions (
    id INT IDENTITY(1,1) PRIMARY KEY,
    agent_id INT FOREIGN KEY REFERENCES agents(id),
    user_id INT FOREIGN KEY REFERENCES users(id),
    input_data NVARCHAR(MAX),
    output_data NVARCHAR(MAX),
    status NVARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    execution_time_ms INT,
    tokens_used INT,
    cost DECIMAL(10,6) DEFAULT 0.0,
    error_message NVARCHAR(MAX),
    metadata NVARCHAR(MAX), -- JSON with additional execution info
    started_at DATETIME2 DEFAULT GETUTCDATE(),
    completed_at DATETIME2
);
GO

-- Costs table
CREATE TABLE costs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT FOREIGN KEY REFERENCES users(id),
    agent_id INT FOREIGN KEY REFERENCES agents(id),
    tool_id INT FOREIGN KEY REFERENCES tools(id),
    execution_id INT FOREIGN KEY REFERENCES executions(id),
    cost_type NVARCHAR(50) NOT NULL, -- 'llm_call', 'tool_call', 'storage', etc.
    amount DECIMAL(10,6) NOT NULL,
    currency NVARCHAR(3) DEFAULT 'USD',
    tokens_input INT DEFAULT 0,
    tokens_output INT DEFAULT 0,
    description NVARCHAR(500),
    created_at DATETIME2 DEFAULT GETUTCDATE()
);
GO

-- Create indexes for performance
CREATE INDEX IX_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IX_api_keys_api_key ON api_keys(api_key);
CREATE INDEX IX_encrypted_credentials_user_id ON encrypted_credentials(user_id);
CREATE INDEX IX_agents_created_by ON agents(created_by);
CREATE INDEX IX_executions_agent_id ON executions(agent_id);
CREATE INDEX IX_executions_user_id ON executions(user_id);
CREATE INDEX IX_executions_created_at ON executions(started_at);
CREATE INDEX IX_costs_user_id ON costs(user_id);
CREATE INDEX IX_costs_created_at ON costs(created_at);
GO

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('default_model', 'gpt-3.5-turbo', 'Default OpenAI model for new agents'),
('max_agents_per_user', '10', 'Maximum number of agents per user'),
('max_executions_per_hour', '100', 'Maximum executions per hour per user'),
('hot_reload_enabled', 'true', 'Enable hot reload of configuration changes');
GO

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, full_name, role) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewMwIrm4DpGX.Nue', 'System Administrator', 'Admin');
GO

PRINT 'Database and tables created successfully!';
GO