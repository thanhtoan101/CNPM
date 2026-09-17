import { useMemo, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import type { LucideIcon } from "lucide-react";
import {
  Archive,
  BarChart3,
  Bell,
  Boxes,
  Camera,
  Check,
  ChevronRight,
  CircleDollarSign,
  ClipboardCheck,
  Clock3,
  FileImage,
  Filter,
  Gauge,
  LayoutDashboard,
  ListFilter,
  Menu,
  MessageSquareWarning,
  PackageCheck,
  Search,
  Settings,
  ShieldCheck,
  ShoppingBag,
  UploadCloud,
  UserRoundCheck,
  Users,
  X,
} from "lucide-react";
import { orders } from "./data";
import { useDemo } from "./DemoStore";
import { advanceOrder as advanceDemoOrder, money, orderValue } from "./domain";
import { ScanDelivery, ServicesPage, CustomersPage, ReportsPage, ApprovalsPage, ApprovalTable, ModerationPage, MarketplacePage, ArchivePage, SettingsPage } from "./FeaturePages";
import type { Order, OrderStatus } from "./data";

type PortalRole = "lab" | "admin";
type PageId =
  | "dashboard"
  | "orders"
  | "processing"
  | "scans"
  | "services"
  | "customers"
  | "reports"
  | "approvals"
  | "moderation"
  | "marketplace"
  | "archive"
  | "settings";

type NavigationItem = { id: PageId; label: string; icon: LucideIcon };

const labNavigation: NavigationItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "orders", label: "Orders", icon: Boxes },
  { id: "processing", label: "Processing board", icon: Gauge },
  { id: "scans", label: "Scan delivery", icon: UploadCloud },
  { id: "services", label: "Services & pricing", icon: CircleDollarSign },
  { id: "customers", label: "Customers", icon: Users },
  { id: "reports", label: "Reports", icon: BarChart3 },
];

const adminNavigation: NavigationItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "approvals", label: "Lab approvals", icon: UserRoundCheck },
  { id: "moderation", label: "Moderation", icon: ShieldCheck },
  { id: "marketplace", label: "Marketplace", icon: ShoppingBag },
  { id: "archive", label: "Digital archive", icon: Archive },
  { id: "customers", label: "Users & roles", icon: Users },
  { id: "reports", label: "Reports", icon: BarChart3 },
];

const nextStatus: Partial<Record<OrderStatus, OrderStatus>> = {
  New: "Film received",
  "Film received": "Developing",
  Developing: "Scanning",
  Scanning: "Quality check",
  "Quality check": "Completed",
};

const pageTitles: Record<PageId, string> = {
  dashboard: "Operations dashboard",
  orders: "Customer orders",
  processing: "Processing board",
  scans: "Scan delivery",
  services: "Services and pricing",
  customers: "Customers and roles",
  reports: "Performance reports",
  approvals: "Film Lab approvals",
  moderation: "Moderation queue",
  marketplace: "Marketplace listings",
  archive: "Digital Film Archive",
  settings: "Portal settings",
};

function App() {
  const [role, setRole] = useState<PortalRole>("lab");
  const [page, setPage] = useState<PageId>("dashboard");
  const [menuOpen, setMenuOpen] = useState(false);
  const { state, update, error } = useDemo();
  const orderData = state.orders;
  const [selectedId, setSelectedId] = useState(orders[0]?.id ?? "");
  const selectedOrder = orderData.find(item => item.id === selectedId) ?? null;
  const setSelectedOrder = (order: Order | null) => setSelectedId(order?.id ?? "");
  const [toast, setToast] = useState("");

  const switchRole = (nextRole: PortalRole) => {
    setRole(nextRole);
    setPage("dashboard");
    setMenuOpen(false);
  };

  const navigate = (nextPage: PageId) => {
    setPage(nextPage);
    setMenuOpen(false);
  };

  const notify = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(""), 2600);
  };

  const advanceOrder = (order: Order) => {
    try {
      const next = advanceDemoOrder(state, order.id);
      if (update(() => next)) { setSelectedId(order.id); notify(`${order.id} updated and saved locally`); }
    } catch (error) { notify((error as Error).message); }
  };

  return (
    <div className="app-shell">
      <Sidebar
        role={role}
        page={page}
        open={menuOpen}
        onNavigate={navigate}
        onClose={() => setMenuOpen(false)}
      />
      <main className="workspace">
        <Header
          title={pageTitles[page]}
          role={role}
          onRoleChange={switchRole}
          onMenu={() => setMenuOpen(true)}
        />
        <div className="page-content">
          <p className="demo-banner">Interactive coursework demo · Changes are saved in this browser · Role switching is for demonstration; shared API authentication is not connected.</p>
          {error && <p role="alert" className="form-error">{error}</p>}
          {page === "dashboard" && (
            <Dashboard role={role} orders={orderData} onNavigate={navigate} onSelect={setSelectedOrder} />
          )}
          {page === "orders" && (
            <OrdersPage
              orders={orderData}
              selected={selectedOrder}
              onSelect={setSelectedOrder}
              onAdvance={advanceOrder}
            />
          )}
          {page === "processing" && <ProcessingBoard orders={orderData} onAdvance={advanceOrder} />}
          {page === "scans" && <ScanDelivery onNotify={notify} />}
          {page === "services" && <ServicesPage onNotify={notify} />}
          {page === "customers" && <CustomersPage role={role} />}
          {page === "reports" && <ReportsPage role={role} />}
          {page === "approvals" && <ApprovalsPage onNotify={notify} />}
          {page === "moderation" && <ModerationPage onNotify={notify} />}
          {page === "marketplace" && <MarketplacePage onNotify={notify} />}
          {page === "archive" && <ArchivePage />}
          {page === "settings" && <SettingsPage onNotify={notify} />}
        </div>
      </main>
      {toast && (
        <div className="toast" role="status">
          <Check size={18} aria-hidden="true" /> {toast}
        </div>
      )}
    </div>
  );
}

function Sidebar({
  role,
  page,
  open,
  onNavigate,
  onClose,
}: {
  role: PortalRole;
  page: PageId;
  open: boolean;
  onNavigate: (page: PageId) => void;
  onClose: () => void;
}) {
  const navigation = role === "lab" ? labNavigation : adminNavigation;
  return (
    <>
      <button className={`sidebar-scrim ${open ? "is-open" : ""}`} aria-label="Close navigation" onClick={onClose} />
      <aside className={`sidebar ${open ? "is-open" : ""}`}>
        <div className="brand">
          <span className="brand-mark"><Camera size={21} /></span>
          <span><strong>FilmOps</strong><small>{role === "lab" ? "Lab portal" : "Admin portal"}</small></span>
          <button className="icon-button sidebar-close" title="Close navigation" onClick={onClose}><X size={18} /></button>
        </div>
        <nav aria-label="Primary navigation">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`nav-item ${page === item.id ? "is-active" : ""}`}
                onClick={() => onNavigate(item.id)}
              >
                <Icon size={18} aria-hidden="true" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
        <div className="sidebar-footer">
          <button className={`nav-item ${page === "settings" ? "is-active" : ""}`} onClick={() => onNavigate("settings")}>
            <Settings size={18} aria-hidden="true" /><span>Settings</span>
          </button>
          <div className="profile-mini">
            <span className="avatar">KD</span>
            <span><strong>Khanh Dao</strong><small>{role === "lab" ? "Lab owner" : "System admin"}</small></span>
          </div>
        </div>
      </aside>
    </>
  );
}

function Header({
  title,
  role,
  onRoleChange,
  onMenu,
}: {
  title: string;
  role: PortalRole;
  onRoleChange: (role: PortalRole) => void;
  onMenu: () => void;
}) {
  return (
    <header className="topbar">
      <div className="topbar-title">
        <button className="icon-button menu-button" title="Open navigation" onClick={onMenu}><Menu size={20} /></button>
        <div><span className="eyebrow">FilmOps · Local prototype</span><h1>{title}</h1></div>
      </div>
      <div className="topbar-actions">
        <div className="role-switch" aria-label="Portal role">
          <button className={role === "lab" ? "is-active" : ""} onClick={() => onRoleChange("lab")}>Film Lab</button>
          <button className={role === "admin" ? "is-active" : ""} onClick={() => onRoleChange("admin")}>Admin</button>
        </div>
        <span className="demo-label">Local demo</span>
      </div>
    </header>
  );
}

function Dashboard({
  role,
  orders: orderData,
  onNavigate,
  onSelect,
}: {
  role: PortalRole;
  orders: Order[];
  onNavigate: (page: PageId) => void;
  onSelect: (order: Order) => void;
}) {
  const { state } = useDemo();
  if (role === "admin") {
    return (
      <>
        <section className="section-heading">
          <div><p className="eyebrow">Platform overview</p><h2>Work requiring attention</h2></div>
          <button className="secondary-button" onClick={() => onNavigate("reports")}><BarChart3 size={17} /> View reports</button>
        </section>
        <div className="metric-grid">
          <Metric icon={UserRoundCheck} label="Lab approvals" value={String(state.applications.filter(item => item.status === "Pending").length)} detail="Sample applications awaiting review" tone="teal" />
          <Metric icon={MessageSquareWarning} label="Open reports" value={String(state.reports.filter(item => item.status === "Open").length)} detail="Unresolved sample reports" tone="red" />
          <Metric icon={CircleDollarSign} label="Audit events" value={String(state.audit.length)} detail="Local actions recorded" tone="amber" />
          <Metric icon={Users} label="Listed equipment" value={String(state.listings.filter(item => item.status !== "Hidden").length)} detail="Visible sample listings" tone="green" />
        </div>
        <div className="dashboard-grid">
          <section className="panel table-panel">
            <PanelHeader title="Latest Film Lab applications" action="Review all" onAction={() => onNavigate("approvals")} />
            <ApprovalTable compact />
          </section>
          <section className="attention-panel">
            <div className="attention-copy"><p className="eyebrow">Moderation</p><h2>Resolve high-priority reports first</h2><p>Review the sample evidence and record a reason for each moderation decision.</p><button className="primary-button" onClick={() => onNavigate("moderation")}><ShieldCheck size={17} /> Open queue</button></div>
            <img src="/images/analog-workspace.png" alt="Analog camera, film negatives, and printed photographs" />
          </section>
        </div>
      </>
    );
  }

  const active = orderData.filter((item) => item.status !== "Completed");
  return (
    <>
      <section className="section-heading">
        <div><p className="eyebrow">Current sample workload</p><h2>Good afternoon, Khanh</h2><p>{active.length} orders are active in this browser.</p></div>
        <button className="primary-button" onClick={() => onNavigate("orders")}><Boxes size={17} /> Review new orders</button>
      </section>
      <div className="metric-grid">
        <Metric icon={Boxes} label="New orders" value={String(orderData.filter(item => item.status === "New").length)} detail="Waiting for film receipt" tone="teal" />
        <Metric icon={Clock3} label="Active orders" value={String(active.length)} detail="Orders not yet completed" tone="amber" />
        <Metric icon={FileImage} label="At quality check" value={String(orderData.filter(item => item.status === "Quality check").length)} detail="Review scans before publication" tone="green" />
        <Metric icon={CircleDollarSign} label="Completed order value" value={money(orderData.filter(item => item.status === "Completed").reduce((sum, item) => sum + orderValue(item), 0))} detail="Sample totals, not collected payments" tone="red" />
      </div>
      <div className="dashboard-grid">
        <section className="panel table-panel">
          <PanelHeader title="Orders in progress" action="View all" onAction={() => onNavigate("orders")} />
          <div className="table-wrap">
            <table>
              <thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Due</th><th><span className="sr-only">Open</span></th></tr></thead>
              <tbody>
                {active.slice(0, 5).map((order) => (
                  <tr key={order.id} tabIndex={0} onKeyDown={event => { if (event.key === "Enter") { onSelect(order); onNavigate("orders"); } }} onClick={() => { onSelect(order); onNavigate("orders"); }}>
                    <td><strong>{order.id}</strong><small>{order.service}</small></td>
                    <td>{order.customer}</td><td><StatusBadge status={order.status} /></td><td>{order.due}</td>
                    <td><ChevronRight size={17} aria-hidden="true" /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
        <section className="visual-panel">
          <img src="/images/analog-workspace.png" alt="Analog camera, film negatives, and printed photographs" />
          <div className="visual-caption"><span className="eyebrow">Scan room</span><strong>{orderData.filter(item => item.status === "Scanning").length} orders at scanning</strong><button onClick={() => onNavigate("scans")}>Open scan delivery <ChevronRight size={15} /></button></div>
        </section>
      </div>
    </>
  );
}

function Metric({ icon: Icon, label, value, detail, tone }: { icon: LucideIcon; label: string; value: string; detail: string; tone: string }) {
  return <article className="metric-card"><span className={`metric-icon ${tone}`}><Icon size={19} /></span><div><p>{label}</p><strong>{value}</strong><small>{detail}</small></div></article>;
}

function OrdersPage({
  orders: orderData,
  selected,
  onSelect,
  onAdvance,
}: {
  orders: Order[];
  selected: Order | null;
  onSelect: (order: Order) => void;
  onAdvance: (order: Order) => void;
}) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState("All statuses");
  const filtered = useMemo(() => orderData.filter((order) => {
    const matchesQuery = `${order.id} ${order.customer} ${order.service}`.toLowerCase().includes(query.toLowerCase());
    return matchesQuery && (filter === "All statuses" || order.status === filter);
  }), [filter, orderData, query]);

  return (
    <div className="split-workspace">
      <section className="panel table-panel order-list-panel">
        <div className="toolbar">
          <label className="search-field"><Search size={17} /><span className="sr-only">Search orders</span><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search order or customer" /></label>
          <label className="select-field"><Filter size={16} /><span className="sr-only">Filter by status</span><select value={filter} onChange={(event) => setFilter(event.target.value)}><option>All statuses</option>{Object.keys(nextStatus).map((status) => <option key={status}>{status}</option>)}<option>Completed</option></select></label>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Order</th><th>Customer</th><th>Rolls</th><th>Status</th><th>Due</th></tr></thead>
            <tbody>
              {filtered.map((order) => <tr key={order.id} tabIndex={0} onKeyDown={event => { if (event.key === "Enter") onSelect(order); }} className={selected?.id === order.id ? "selected-row" : ""} onClick={() => onSelect(order)}><td><strong>{order.id}</strong><small>{order.service}</small></td><td>{order.customer}</td><td>{order.rolls}</td><td><StatusBadge status={order.status} /></td><td>{order.due}</td></tr>)}
            </tbody>
          </table>
          {!filtered.length && <EmptyState icon={Search} title="No matching orders" detail="Change the search term or remove a status filter." />}
        </div>
      </section>
      <aside className="detail-pane">
        {selected ? <OrderDetail order={selected} onAdvance={onAdvance} /> : <EmptyState icon={Boxes} title="Select an order" detail="Order details and status history will appear here." />}
      </aside>
    </div>
  );
}

function OrderDetail({ order, onAdvance }: { order: Order; onAdvance: (order: Order) => void }) {
  const next = nextStatus[order.status];
  return <div><div className="detail-heading"><span><p className="eyebrow">Processing order</p><h2>{order.id}</h2></span><StatusBadge status={order.status} /></div><dl className="detail-list"><div><dt>Customer</dt><dd>{order.customer}</dd></div><div><dt>Service</dt><dd>{order.service}</dd></div><div><dt>Film quantity</dt><dd>{order.rolls} roll{order.rolls > 1 ? "s" : ""}</dd></div><div><dt>Due</dt><dd>{order.due}</dd></div><div><dt>Total</dt><dd>{order.price}</dd></div></dl>{order.note && <div className="customer-note"><MessageSquareWarning size={17} /><span><strong>Customer note</strong><p>{order.note}</p></span></div>}<div className="timeline"><strong>Status history</strong><div className="timeline-item is-done"><Check size={13} /><span>Order submitted<small>Sep 10, 09:14</small></span></div><div className="timeline-item is-done"><Check size={13} /><span>Order confirmed<small>Sep 10, 09:20</small></span></div><div className="timeline-item"><Clock3 size={13} /><span>{order.status}<small>Current stage</small></span></div></div>{next ? <button className="primary-button full-button" onClick={() => onAdvance(order)}><PackageCheck size={17} /> Move to {next}</button> : <button className="secondary-button full-button" disabled><Check size={17} /> Order completed</button>}</div>;
}

function ProcessingBoard({ orders: orderData, onAdvance }: { orders: Order[]; onAdvance: (order: Order) => void }) {
  const stages: OrderStatus[] = ["New", "Film received", "Developing", "Scanning", "Quality check", "Completed"];
  return <div className="board-scroll"><div className="processing-board">{stages.map((stage) => { const stageOrders = orderData.filter((item) => item.status === stage); return <section className="board-column" key={stage}><header><span>{stage}</span><small>{stageOrders.length}</small></header><div className="board-list">{stageOrders.map((order) => <article className="order-card" key={order.id}><div><strong>{order.id}</strong><small>{order.customer}</small></div><p>{order.service}</p><footer><span><Clock3 size={14} /> {order.due}</span>{nextStatus[order.status] && <button className="icon-button small" title={`Move ${order.id} to ${nextStatus[order.status]}`} onClick={() => onAdvance(order)}><ChevronRight size={16} /></button>}</footer></article>)}</div></section>; })}</div></div>;
}

function PanelHeader({ title, action, onAction }: { title: string; action: string; onAction: () => void }) {
  return <div className="panel-header"><h2>{title}</h2><button onClick={onAction}>{action} <ChevronRight size={15} /></button></div>;
}

function StatusBadge({ status }: { status: string }) {
  const className = status.toLowerCase().replaceAll(" ", "-").replaceAll("&", "and");
  return <span className={`status-badge status-${className}`}>{status}</span>;
}

function EmptyState({ icon: Icon, title, detail }: { icon: LucideIcon; title: string; detail: string }) {
  return <div className="empty-state"><Icon size={25} /><strong>{title}</strong><p>{detail}</p></div>;
}

export default App;
