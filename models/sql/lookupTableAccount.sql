CREATE TABLE IF NOT EXISTS lookupTableAccount(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_account INTEGER NOT NULL,
    -- FOREIGN KEY(id_account) REFERENCES account(id),
    lookup_account_name TEXT NOT NULL UNIQUE,
    FOREIGN KEY(id_account) REFERENCES account(id)
);