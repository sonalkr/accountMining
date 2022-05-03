CREATE TABLE IF NOT EXISTS material(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    typeof TEXT NOT NULL,
    material_name TEXT NOT NULL UNIQUE,
    CONSTRAINT chk_t_typeof CHECK (typeof in ("material", "shipping_address"))
);