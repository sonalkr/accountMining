CREATE TABLE IF NOT EXISTS lookupTableMaterial(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_material INTEGER NOT NULL,
    -- FOREIGN KEY(id_account) REFERENCES account(id),
    lookup_material_name TEXT NOT NULL UNIQUE,
    FOREIGN KEY(id_material) REFERENCES material(id)
);