CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    phone_hash TEXT UNIQUE,
    full_name TEXT NOT NULL,
    city TEXT,
    lat REAL,
    lon REAL,
    skills TEXT,
    hobbies TEXT,
    language TEXT DEFAULT 'ru',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS connections (
    connection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_from INTEGER NOT NULL,
    user_to INTEGER NOT NULL,
    status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);