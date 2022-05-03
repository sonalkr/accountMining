CREATE TABLE IF NOT EXISTS sale(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_ INTEGER NOT NULL CHECK(typeof(date_) = 'integer'),
    challan_no TEXT NOT NULL,
    id_site INTEGER,
    -- FOREIGN KEY(id_site) REFERENCES site(id),
    id_account INTEGER NOT NULL,
    -- FOREIGN KEY(id_account) REFERENCES account(id),
    id_material INTEGER,
    -- FOREIGN KEY(id_material) REFERENCES material(id),
    qty_cft REAL DEFAULT 0,
    qty_ton REAL DEFAULT 0,
    truck_no TEXT,
    transporter_name TEXT,
    id_shipping_address INTEGER,
    bank_sale DECIMAL(16, 2) DEFAULT 0,
    bank_received DECIMAL(16, 2) DEFAULT 0,
    cash_received DECIMAL(16, 2) DEFAULT 0,
    remarks TEXT,
    _id_rate_material INTEGER,
    -- FOREIGN KEY(_id_rate_material) REFERENCES rate(id),
    _sale_amount DECIMAL(16, 2) DEFAULT 0,
    _id_rate_shipping INTEGER,
    -- FOREIGN KEY(_id_rate_shipping) REFERENCES rate(id),
    _shipping_amount DECIMAL(16, 2) DEFAULT 0,
    _total_amount DECIMAL(16, 2) DEFAULT 0,

    -- is_manual_sale BOOLEAN CHECK(is_manual_sale IN (0, 1)) NOT NULL,
    is_manual BOOLEAN CHECK(is_manual IN (0, 1)) NOT NULL,
    _id_unit_material INTEGER,
    -- FOREIGN KEY(_id_unit_material) REFERENCES unit(id),
    _id_unit_shipping INTEGER,
    -- FOREIGN KEY(_id_unit_shipping) REFERENCES unit(id),


    FOREIGN KEY(id_account) REFERENCES account(id),
    FOREIGN KEY(id_material) REFERENCES material(id),
    FOREIGN KEY(id_shipping_address) REFERENCES material(id),
    FOREIGN KEY(_id_rate_material) REFERENCES rate(id),
    FOREIGN KEY(_id_rate_shipping) REFERENCES rate(id),
    FOREIGN KEY(id_site) REFERENCES site_(id),
    FOREIGN KEY(_id_unit_shipping) REFERENCES unit(id),
    FOREIGN KEY(_id_unit_material) REFERENCES unit(id)
);