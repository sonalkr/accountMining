CREATE TABLE IF NOT EXISTS rate(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_ INTEGER NOT NULL CHECK(typeof(date_) = 'integer'),
    id_account INTEGER NOT NULL,
    -- FOREIGN KEY(id_account) REFERENCES account(id),
    id_material INTEGER NOT NULL,
    -- FOREIGN KEY(id_material) REFERENCES material(id),
    id_unit INTEGER NOT NULL,
    -- FOREIGN KEY(id_unit) REFERENCES unit(id),
    amount REAL DEFAULT 0,
    FOREIGN KEY(id_account) REFERENCES account(id),
    FOREIGN KEY(id_material) REFERENCES material(id),
    FOREIGN KEY(id_unit) REFERENCES unit(id)
);