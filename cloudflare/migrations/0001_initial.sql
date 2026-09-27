PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS sites (
 id INTEGER PRIMARY KEY AUTOINCREMENT, site TEXT NOT NULL, domain TEXT NOT NULL,
 country TEXT DEFAULT '', da TEXT DEFAULT '', dr TEXT DEFAULT '', traffic TEXT DEFAULT '',
 general_price TEXT DEFAULT '', casino_price TEXT DEFAULT '', payment_method TEXT DEFAULT '',
 tat TEXT DEFAULT '', type TEXT DEFAULT '', link_type TEXT DEFAULT '', source_file TEXT DEFAULT '',
 sheet_name TEXT DEFAULT '', favorite INTEGER DEFAULT 0, created_at TEXT NOT NULL,
 original_price TEXT DEFAULT '', selling_price TEXT DEFAULT '', markup_percent REAL DEFAULT 20,
 manual_price INTEGER DEFAULT 0, casino_original_price TEXT DEFAULT '', casino_selling_price TEXT DEFAULT '',
 niche TEXT DEFAULT 'General', da_value REAL, dr_value REAL, traffic_value REAL, price_value REAL,
 original_value REAL, casino_original_value REAL
);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_sites_country ON sites(country,id);
CREATE INDEX IF NOT EXISTS idx_sites_dr ON sites(dr_value,id);
CREATE INDEX IF NOT EXISTS idx_sites_price ON sites(price_value,id);
CREATE INDEX IF NOT EXISTS idx_sites_source ON sites(source_file,sheet_name,id);
CREATE TABLE IF NOT EXISTS favorites(domain TEXT PRIMARY KEY,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS deleted_sites(domain TEXT NOT NULL,source_file TEXT NOT NULL,sheet_name TEXT NOT NULL,deleted_at TEXT NOT NULL,PRIMARY KEY(domain,source_file,sheet_name));
CREATE TABLE IF NOT EXISTS reseller_settings(source_file TEXT NOT NULL,sheet_name TEXT NOT NULL,markup_percent REAL DEFAULT 20,updated_at TEXT NOT NULL,PRIMARY KEY(source_file,sheet_name));
CREATE TABLE IF NOT EXISTS contacts(domain TEXT PRIMARY KEY,admin_name TEXT,email TEXT,whatsapp TEXT,telegram TEXT,status TEXT,quoted_price TEXT,notes TEXT,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS contact_messages(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,email TEXT,phone TEXT,company TEXT,website TEXT,subject TEXT,message TEXT NOT NULL,status TEXT DEFAULT 'New',created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS team_members(id INTEGER PRIMARY KEY AUTOINCREMENT,full_name TEXT NOT NULL,designation TEXT NOT NULL,level TEXT NOT NULL,reports_to TEXT,email TEXT,phone TEXT,linkedin TEXT,website TEXT,location TEXT,bio TEXT,skills TEXT,image_path TEXT,display_order INTEGER DEFAULT 100,active INTEGER DEFAULT 1,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS reseller_private(id INTEGER PRIMARY KEY AUTOINCREMENT,source_file TEXT NOT NULL,sheet_name TEXT,field_name TEXT NOT NULL,field_value TEXT,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sheet_structure(source_file TEXT NOT NULL,sheet_name TEXT NOT NULL,header_row INTEGER,status TEXT,mapped_fields TEXT,private_count INTEGER DEFAULT 0,updated_at TEXT NOT NULL,PRIMARY KEY(source_file,sheet_name));
CREATE TABLE IF NOT EXISTS outreach_pipeline(id INTEGER PRIMARY KEY AUTOINCREMENT,site_id INTEGER,site TEXT NOT NULL UNIQUE,status TEXT NOT NULL DEFAULT 'New',contact_name TEXT,contact_email TEXT,whatsapp TEXT,last_contacted TEXT,next_follow_up TEXT,notes TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS admin_private_contacts(id INTEGER PRIMARY KEY AUTOINCREMENT,contact_type TEXT NOT NULL,full_name TEXT NOT NULL,company TEXT,job_title TEXT,email TEXT,phone TEXT,whatsapp TEXT,website TEXT,linkedin TEXT,address TEXT,notes TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS import_review(id INTEGER PRIMARY KEY,site TEXT,source_file TEXT,sheet_name TEXT,reason TEXT,raw_record TEXT NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS media(key TEXT PRIMARY KEY,content_type TEXT NOT NULL,data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS auth_users(username TEXT PRIMARY KEY,salt TEXT NOT NULL,password_hash TEXT NOT NULL,iterations INTEGER NOT NULL DEFAULT 600000);
CREATE TABLE IF NOT EXISTS sessions(token_hash TEXT PRIMARY KEY,username TEXT NOT NULL,expires_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
CREATE TABLE IF NOT EXISTS rate_limits(key TEXT PRIMARY KEY,count INTEGER NOT NULL,expires_at INTEGER NOT NULL);
CREATE INDEX IF NOT EXISTS idx_limits_expires ON rate_limits(expires_at);
CREATE TABLE IF NOT EXISTS app_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);
INSERT OR IGNORE INTO app_meta VALUES('version','1');
