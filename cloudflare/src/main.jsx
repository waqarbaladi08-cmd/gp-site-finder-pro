import React, { useEffect, useState, Suspense, lazy } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard,
  Search,
  Bookmark,
  Mail,
  ChevronDown,
  Menu,
  X,
  ArrowUpRight,
  ShieldCheck,
  LogOut,
  Globe2,
  BarChart3,
  Upload,
  PlusCircle,
  Database,
  Users,
  Settings,
  Contact,
  Cloud,
  FileSpreadsheet,
  Download,
  CopyCheck,
  BriefcaseBusiness,
  UserCircle,
  KeyRound,
  ArrowRight,
} from "lucide-react";
import {
  AppContext,
  useApp,
  useData,
  api,
  appPath,
  Loading,
  ErrorBox,
  Heading,
  AdminGate,
  formatNumber,
} from "./lib.jsx";
import { SearchPage, SiteTable } from "./sites.jsx";
import { stripAppBase } from "../shared/routing.mjs";
import "./style.css";
const modulePage = (file, name) =>
  lazy(() => file().then((m) => ({ default: m[name] })));
const ResourcePage = modulePage(
    () => import("./resources.jsx"),
    "ResourcePage",
  ),
  TeamPage = modulePage(() => import("./resources.jsx"), "TeamPage"),
  ContactPage = modulePage(() => import("./resources.jsx"), "ContactPage"),
  ProfilePage = modulePage(() => import("./resources.jsx"), "ProfilePage"),
  SettingsPage = modulePage(() => import("./resources.jsx"), "SettingsPage"),
  LoginPage = modulePage(() => import("./resources.jsx"), "LoginPage");
const OutreachPage = modulePage(() => import("./tools.jsx"), "OutreachPage"),
  ContactAnalyzer = modulePage(() => import("./contact-analyzer.jsx"), "ContactAnalyzer"),
  ImportPage = modulePage(() => import("./tools.jsx"), "ImportPage"),
  ExportPage = modulePage(() => import("./tools.jsx"), "ExportPage"),
  BackupPage = modulePage(() => import("./tools.jsx"), "BackupPage"),
  DuplicatesPage = modulePage(() => import("./tools.jsx"), "DuplicatesPage"),
  PricingPage = modulePage(() => import("./tools.jsx"), "PricingPage"),
  CloudPage = modulePage(() => import("./tools.jsx"), "CloudPage"),
  MetricsPage = modulePage(() => import("./tools.jsx"), "MetricsPage");
const primary = [
  ["home", "Dashboard", LayoutDashboard],
  ["search", "Search websites", Search],
  ["saved", "Saved websites", Bookmark],
  ["outreach", "Publisher outreach", Mail],
  ["team", "Our team", Users],
];
const groups = [
  [
    "Research tools",
    [
      ["client-outreach", "Client outreach", BriefcaseBusiness],
      ["export", "Export results", Download],
      ["statistics", "Statistics", BarChart3],
      ["metrics", "Real metrics", Globe2],
    ],
  ],
  [
    "Manage workspace",
    [
      ["manage", "Manage websites", Database],
      ["import", "Import Excel", Upload],
      ["pipeline", "Outreach pipeline", Mail],
      ["contacts", "Private contacts", Contact],
      ["contact-analyzer", "Contact Analyzer", FileSpreadsheet],
      ["resellers", "Reseller details", BriefcaseBusiness],
      ["pricing", "Price manager", FileSpreadsheet],
      ["duplicates", "Duplicate finder", CopyCheck],
      ["structures", "Sheet scanner", FileSpreadsheet],
      ["review", "Import review", FileSpreadsheet],
      ["vault", "Contact vault", KeyRound],
      ["messages", "Contact inbox", Mail],
      ["cloud", "Cloud storage", Cloud],
      ["backup", "Backup & restore", Download],
      ["settings", "Settings", Settings],
    ],
  ],
  [
    "Business",
    [
      ["contact", "Contact us", Mail],
      ["profile", "Profile & contact", UserCircle],
    ],
  ],
];
const labels = Object.fromEntries(
  [
    ...primary,
    ...groups.flatMap((g) => g[1]),
    ["login", "Admin sign in"],
    ["team-admin", "Manage team"],
  ].map(([p, l]) => [p, l]),
);
const legacy = {
  Dashboard: "home",
  "Search Websites": "search",
  Favorites: "saved",
  "Outreach Generator": "outreach",
  "Client Outreach Generator": "client-outreach",
  "Import Excel": "import",
  "Export Results": "export",
  "Real Metrics Search": "metrics",
  Statistics: "statistics",
  "Add New Site": "manage",
  "Edit Site": "manage",
  "Delete Site": "manage",
  "Duplicate Finder": "duplicates",
  "Private Contacts": "contacts",
  "Reseller Private Details": "resellers",
  "Reseller Price Manager": "pricing",
  "Sheet Structure Scanner": "structures",
  "Cloud Sync": "cloud",
  "Admin Contact Vault": "vault",
  "Our Team": "team",
  "Contact Us": "contact",
  "My Profile / Contact": "profile",
  "Backup & Restore": "backup",
  Settings: "settings",
  "Admin Login": "login",
  "Outreach Pipeline": "pipeline",
};
function currentPage() {
  const query = new URLSearchParams(location.search).get("page");
  const p = query
    ? legacy[query] || query
    : stripAppBase(location.pathname).replace(/^\/+|\/+$/g, "") || "home";
  return labels[p] ? p : "home";
}
function Dashboard({ statistics = false }) {
  const { data, loading, error } = useData("/api/stats"),
    { go, saved } = useApp();
  return (
    <>
      <Heading
        eyebrow={statistics ? "DATABASE OVERVIEW" : "YOUR PUBLISHER WORKSPACE"}
        title={
          statistics
            ? "Directory statistics"
            : "Find the right place for your next story."
        }
        actions={
          <button className="primary" onClick={() => go("search")}>
            Find websites <ArrowRight size={17} />
          </button>
        }
      >
        {statistics
          ? "A current view of the websites and recorded metrics in your directory."
          : "Discover publishers, compare opportunities and build better outreach—all in one place."}
      </Heading>
      <ErrorBox error={error} />
      {loading ? (
        <Loading />
      ) : (
        data && (
          <>
            <div className="stats-grid">
              <div className="stat-card">
                <span className="stat-icon">
                  <Globe2 size={20} />
                </span>
                <small>Website listings</small>
                <strong>{formatNumber(data.total)}</strong>
                <span>{formatNumber(data.domains)} unique domains</span>
              </div>
              <div className="stat-card">
                <span className="stat-icon teal">
                  <Globe2 size={20} />
                </span>
                <small>Recorded countries</small>
                <strong>{formatNumber(data.countries)}</strong>
                <span>Based on supplied country labels</span>
              </div>
              <div className="stat-card">
                <span className="stat-icon violet">
                  <BarChart3 size={20} />
                </span>
                <small>Average domain rating</small>
                <strong>{data.average_dr ?? "—"}</strong>
                <span>{formatNumber(data.recorded_dr)} recorded DR values</span>
              </div>
              <div className="stat-card">
                <span className="stat-icon amber">
                  <Bookmark size={20} />
                </span>
                <small>Your saved websites</small>
                <strong>{saved.length}</strong>
                <span>Your shortlist in this browser</span>
              </div>
            </div>
            {!statistics && (
              <div className="quick-grid">
                <button className="quick-card" onClick={() => go("search")}>
                  <Search size={25} />
                  <div>
                    <h3>Discover websites</h3>
                    <p>Filter by niche, country and budget.</p>
                  </div>
                  <ArrowRight size={20} />
                </button>
                <button className="quick-card" onClick={() => go("outreach")}>
                  <Mail size={25} />
                  <div>
                    <h3>Start a conversation</h3>
                    <p>Build a personalized outreach draft.</p>
                  </div>
                  <ArrowRight size={20} />
                </button>
              </div>
            )}
            <div className="breakdowns">
              <section className="panel form-panel">
                <div className="panel-heading flush">
                  <h2>Publisher niches</h2>
                  <span className="subtle">Estimated from listings</span>
                </div>
                {data.niches.slice(0, statistics ? 20 : 6).map((r) => (
                  <div className="bar-row" key={r.name}>
                    <div>
                      <span>{r.name}</span>
                      <strong>{r.count.toLocaleString()}</strong>
                    </div>
                    <div className="bar-track">
                      <span
                        style={{
                          width: `${Math.max(1, (r.count / (data.niches[0]?.count || 1)) * 100)}%`,
                        }}
                      />
                    </div>
                  </div>
                ))}
              </section>
              <section className="panel form-panel">
                <div className="panel-heading flush">
                  <h2>Country coverage</h2>
                </div>
                {data.countries_breakdown
                  .slice(0, statistics ? 12 : 6)
                  .map((r) => (
                    <div className="country-row" key={r.name}>
                      <span>
                        <Globe2 size={16} />
                        {r.name}
                      </span>
                      <strong>{r.count.toLocaleString()}</strong>
                    </div>
                  ))}
                <p className="subtle footnote">
                  Countries are taken from supplied data. A domain name alone
                  does not establish a publisher’s location.
                </p>
              </section>
            </div>
            {!statistics && (
              <section className="panel">
                <div className="panel-heading">
                  <h2>Recently added websites</h2>
                  <button className="text-button" onClick={() => go("search")}>
                    Browse directory <ArrowRight size={16} />
                  </button>
                </div>
                <SiteTable rows={data.recent} />
              </section>
            )}
          </>
        )
      )}
    </>
  );
}
function Page({ page }) {
  const admin = (node) => <AdminGate>{node}</AdminGate>;
  if (page === "home" || page === "statistics")
    return <Dashboard statistics={page === "statistics"} />;
  if (page === "search" || page === "saved") return <SearchPage mode={page} />;
  if (page === "manage") return admin(<SearchPage mode="manage" />);
  if (page === "outreach" || page === "client-outreach")
    return <OutreachPage client={page === "client-outreach"} />;
  if (
    [
      "contacts",
      "pipeline",
      "vault",
      "resellers",
      "structures",
      "messages",
      "review",
    ].includes(page)
  )
    return admin(<ResourcePage name={page} />);
  const publicPages = {
    login: <LoginPage />,
    team: <TeamPage />,
    contact: <ContactPage />,
    profile: <ProfilePage />,
    export: <ExportPage />,
  };
  if (publicPages[page]) return publicPages[page];
  const adminPages = {
    "contact-analyzer": <ContactAnalyzer />,
    import: <ImportPage />,
    backup: <BackupPage />,
    duplicates: <DuplicatesPage />,
    pricing: <PricingPage />,
    cloud: <CloudPage />,
    metrics: <MetricsPage />,
    settings: <SettingsPage />,
    "team-admin": <ResourcePage name="team" />,
  };
  return admin(adminPages[page] || <Dashboard />);
}
class ErrorBoundary extends React.Component {
  state = { error: false };
  static getDerivedStateFromError() {
    return { error: true };
  }
  render() {
    return this.state.error ? (
      <div className="panel form-panel">
        <h1>Something went wrong</h1>
        <p>
          Reload to reopen your workspace. Saved data remains in the database.
        </p>
        <button onClick={() => location.reload()}>Reload workspace</button>
      </div>
    ) : (
      this.props.children
    );
  }
}
function App() {
  const [page, setPage] = useState(currentPage),
    [routeKey, setRouteKey] = useState(location.href),
    [mobile, setMobile] = useState(false),
    [revision, setRevision] = useState(0),
    [user, setUser] = useState(null),
    [authLoading, setAuthLoading] = useState(true),
    [toast, setToast] = useState(null);
  const [saved, setSaved] = useState(() => {
    try {
      const v = JSON.parse(localStorage.getItem("gp:saved") || "[]");
      return Array.isArray(v)
        ? [...new Set(v.filter((x) => Number.isInteger(x) && x > 0))].slice(
            0,
            1000,
          )
        : [];
    } catch {
      return [];
    }
  });
  const notify = (message, type = "success") => setToast({ message, type });
  const go = (next, params = {}) => {
    const q = new URLSearchParams(params);
    history.pushState(
      {},
      "",
      appPath(`/${next === "home" ? "" : next}${q.size ? "?" + q : ""}`),
    );
    setPage(next);
    setRouteKey(location.href);
    setMobile(false);
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const loadAuth = async () => {
    try {
      const r = await api("/api/auth/me");
      setUser(r.user);
      return r.user;
    } catch {
      setUser(null);
      return null;
    } finally {
      setAuthLoading(false);
    }
  };
  useEffect(() => {
    loadAuth();
    const pop = () => {
      setPage(currentPage());
      setRouteKey(location.href);
      setMobile(false);
    };
    window.addEventListener("popstate", pop);
    const save = (e) =>
      setSaved((s) =>
        s.includes(e.detail) ? s : [...s, e.detail].slice(0, 1000),
      );
    window.addEventListener("gp:save", save);
    return () => {
      window.removeEventListener("popstate", pop);
      window.removeEventListener("gp:save", save);
    };
  }, []);
  useEffect(() => {
    try {
      localStorage.setItem("gp:saved", JSON.stringify(saved));
    } catch {
      notify(
        "Browser storage is full. Saved websites may not persist.",
        "error",
      );
    }
  }, [saved]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 6500);
    return () => clearTimeout(t);
  }, [toast]);
  useEffect(() => {
    document.title = `${labels[page]} · GP Site Finder Pro`;
  }, [page]);
  const toggleSaved = (id) =>
    setSaved((s) =>
      s.includes(id)
        ? s.filter((v) => v !== id)
        : s.length >= 1000
          ? (notify("Your shortlist can hold 1,000 websites.", "error"), s)
          : [...s, id],
    );
  const nav = ([p, name, Icon]) => (
    <a
      key={p}
      href={appPath("/" + (p === "home" ? "" : p))}
      className={"nav-link " + (page === p ? "current" : "")}
      aria-current={page === p ? "page" : undefined}
      onClick={(e) => {
        if (!e.ctrlKey && !e.metaKey) {
          e.preventDefault();
          go(p);
        }
      }}
    >
      <Icon size={18} />
      <span>{name}</span>
      {p === "saved" && saved.length > 0 && <small>{saved.length}</small>}
    </a>
  );
  return (
    <AppContext.Provider
      value={{
        page,
        go,
        user,
        authLoading,
        loadAuth,
        revision,
        refresh: () => setRevision((v) => v + 1),
        notify,
        saved,
        toggleSaved,
      }}
    >
      <a className="skip" href="#main">
        Skip to content
      </a>
      {mobile && (
        <button
          className="backdrop"
          aria-label="Close navigation"
          onClick={() => setMobile(false)}
        />
      )}
      <aside className={"sidebar " + (mobile ? "is-open" : "")}>
        <a
          href={appPath("/")}
          className="brand"
          onClick={(e) => {
            e.preventDefault();
            go("home");
          }}
        >
          <span className="brand-mark">GP</span>
          <div>
            <strong>Site Finder Pro</strong>
            <small>PUBLISHER WORKSPACE</small>
          </div>
        </a>
        <nav aria-label="Main navigation">
          <p className="nav-label">WORKSPACE</p>
          {primary.map(nav)}
          <details
            className="tools-menu"
            open={
              groups.flatMap((g) => g[1]).some(([p]) => p === page) || undefined
            }
          >
            <summary>
              <span>More tools</span>
              <ChevronDown size={15} />
            </summary>
            {groups.map(([name, links]) => (
              <div key={name} className="nav-group">
                <p className="nav-label">{name}</p>
                {links.filter(([p]) => user || !["contacts", "contact-analyzer", "resellers", "vault"].includes(p)).map(nav)}
              </div>
            ))}
          </details>
        </nav>
        <div className="sidebar-bottom">
          <a
            href="https://gp-site-finder-pro-landing.vercel.app/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Visit website <ArrowUpRight size={15} />
          </a>
          {user ? (
            <>
              <div className="signed-in">
                <ShieldCheck size={17} />
                <div>
                  <strong>{user.username}</strong>
                  <small>Administrator</small>
                </div>
              </div>
              <button
                onClick={async () => {
                  try {
                    await api("/api/auth/logout", { method: "POST", body: {} });
                    await loadAuth();
                    go("home");
                  } catch (e) {
                    notify(e.message, "error");
                  }
                }}
              >
                <LogOut size={16} /> Sign out
              </button>
            </>
          ) : (
            <button onClick={() => go("login")}>
              <ShieldCheck size={17} /> Admin sign in
            </button>
          )}
        </div>
      </aside>
      <div className="workspace">
        <div className="topbar">
          <button
            className="icon mobile-toggle"
            aria-label="Open navigation"
            onClick={() => setMobile(true)}
          >
            <Menu size={23} />
          </button>
          <div className="breadcrumb">
            <span>Workspace</span>
            <span>/</span>
            <strong>{labels[page]}</strong>
          </div>
          <span className="workspace-tag">
            <span />
            {user ? "Administrator" : "Publisher research"}
          </span>
        </div>
        <main id="main" tabIndex="-1">
          <ErrorBoundary key={routeKey}>
            <Suspense fallback={<Loading label="Opening workspace…" />}>
              <Page key={routeKey} page={page} />
            </Suspense>
          </ErrorBoundary>
          <footer>
            GP Site Finder Pro{" "}
            <span>Research with context. Reach out with purpose.</span>
          </footer>
        </main>
      </div>
      {toast && (
        <div
          className={"toast " + toast.type}
          role={toast.type === "error" ? "alert" : "status"}
        >
          <span>{toast.message}</span>
          <button
            className="icon"
            aria-label="Dismiss notification"
            onClick={() => setToast(null)}
          >
            <X size={16} />
          </button>
        </div>
      )}
    </AppContext.Provider>
  );
}
createRoot(document.getElementById("root")).render(<App />);
