ALTER TABLE contacts ADD COLUMN phone TEXT DEFAULT '';
ALTER TABLE contacts ADD COLUMN contact_url TEXT DEFAULT '';
CREATE INDEX IF NOT EXISTS idx_reseller_private_source ON reseller_private(source_file,sheet_name);
