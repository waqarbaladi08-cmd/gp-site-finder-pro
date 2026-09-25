"""Pure helpers for a small navigation menu and honest publisher filters."""
import re
import pandas as pd

PRIMARY_PAGES = (
    ("Dashboard", "Home", ":material/home:"),
    ("Search Websites", "Search", ":material/search:"),
    ("Favorites", "Saved sites", ":material/bookmark:"),
    ("Outreach Generator", "Outreach", ":material/mail:"),
)
TOOL_PAGES = (
    "Import Excel", "Export Results", "Outreach Pipeline", "Client Outreach Generator",
    "Real Metrics Search", "Statistics", "Add New Site", "Edit Site", "Delete Site",
    "Duplicate Finder", "Private Contacts", "Reseller Private Details", "Reseller Price Manager",
    "Sheet Structure Scanner", "Cloud Sync", "Admin Contact Vault", "Our Team", "Contact Us",
    "My Profile / Contact", "Backup & Restore", "Settings", "Admin Login",
)


def resolve_page(value):
    aliases = {"home": "Dashboard", "search": "Search Websites", "saved": "Favorites", "outreach": "Outreach Generator"}
    value = aliases.get(str(value).lower(), str(value))
    allowed = {page for page, _, _ in PRIMARY_PAGES} | set(TOOL_PAGES)
    return value if value in allowed else "Dashboard"


_COUNTRY_GROUPS = {
    "United States": ("us", "usa", "u.s.", "u.s.a.", "united state", "united states", "united states of america"),
    "United Kingdom": ("uk", "u.k.", "gb", "gbr", "united kingdom", "great britain"),
    "Bangladesh": ("bd", "bgd", "bangladesh"),
    "Pakistan": ("pk", "pak", "pakistan"),
    "India": ("in", "ind", "india"),
    "Canada": ("ca", "can", "canada"),
    "Australia": ("au", "aus", "australia"),
    "United Arab Emirates": ("ae", "uae", "u.a.e.", "united arab emirates"),
    "Philippines": ("ph", "phl", "philippines", "phillipines", "philippine"),
    "Indonesia": ("id", "idn", "indonesia"),
    "Germany": ("de", "deu", "germany"),
    "France": ("fr", "fra", "france"),
    "Singapore": ("sg", "sgp", "singapore"),
    "New Zealand": ("nz", "nzl", "new zealand"),
}
_ALIASES = {alias: country for country, aliases in _COUNTRY_GROUPS.items() for alias in aliases}
_MISSING = {"", "unknown", "n/a", "na", "none", "nan", "null", "all", "global", "worldwide", "-", "not specified"}


def normalize_country(value):
    """Normalize explicit labels only. Never infer geography from a domain or niche."""
    if value is None or pd.isna(value):
        return ""
    text = re.sub(r"\s+", " ", str(value)).strip()
    key = text.casefold()
    if key in _MISSING or len(text) > 80 or re.search(r"\d", text):
        return ""
    if not re.fullmatch(r"[A-Za-zÀ-ÿ .,'()&/-]+", text):
        return ""
    return _ALIASES.get(key, text)


def metric_mask(frame, min_dr=0, max_price=0):
    """Unset filters include unknown values; explicit limits require a recorded metric."""
    mask = pd.Series(True, index=frame.index)
    if min_dr > 0:
        mask &= frame["_dr_num"].ge(min_dr).fillna(False)
    if max_price > 0:
        mask &= frame["_price_num"].le(max_price).fillna(False)
    return mask
