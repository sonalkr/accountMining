CREATE TABLE IF NOT EXISTS account(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lookup_id TEXT NOT NULL UNIQUE,
    account_name TEXT NOT NULL UNIQUE,
    id_agent INTEGER,
    op_cash DECIMAL(16, 2) DEFAULT 0,
    op_bank DECIMAL(16, 2) DEFAULT 0,
    _op_total DECIMAL(16, 2) DEFAULT 0,
    _cash_sale DECIMAL(16, 2) DEFAULT 0,
    _bank_sale DECIMAL(16, 2) DEFAULT 0,
    _cash_received DECIMAL(16, 2) DEFAULT 0,
    _bank_received DECIMAL(16, 2) DEFAULT 0,
    _cl_cash DECIMAL(16, 2) DEFAULT 0,
    _cl_bank DECIMAL(16, 2) DEFAULT 0,
    _cl_total DECIMAL(16, 2) DEFAULT 0,
    FOREIGN KEY(id_agent) REFERENCES agent(id)
);