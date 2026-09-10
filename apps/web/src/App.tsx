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
import { approvalQueue, listings, orders, reports } from "./data";
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
  const [orderData, setOrderData] = useState(orders);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(orders[0]);
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
    const status = nextStatus[order.status];
    if (!status) return;
    const updated = { ...order, status };
    setOrderData((current) => current.map((item) => (item.id === order.id ? updated : item)));
    setSelectedOrder(updated);
    notify(`${order.id} moved to ${status}`);
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
        <div><span className="eyebrow">September 10, 2026</span><h1>{title}</h1></div>
      </div>
      <div className="topbar-actions">
        <div className="role-switch" aria-label="Portal role">
          <button className={role === "lab" ? "is-active" : ""} onClick={() => onRoleChange("lab")}>Film Lab</button>
          <button className={role === "admin" ? "is-active" : ""} onClick={() => onRoleChange("admin")}>Admin</button>
        </div>
        <button className="icon-button notification-button" title="Notifications">
          <Bell size={19} /><span className="notification-dot" />
        </button>
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
  if (role === "admin") {
    return (
      <>
        <section className="section-heading">
          <div><p className="eyebrow">Platform overview</p><h2>Work requiring attention</h2></div>
          <button className="secondary-button" onClick={() => onNavigate("reports")}><BarChart3 size={17} /> View reports</button>
        </section>
        <div className="metric-grid">
          <Metric icon={UserRoundCheck} label="Lab approvals" value="3" detail="1 complete application" tone="teal" />
          <Metric icon={MessageSquareWarning} label="Open reports" value="8" detail="2 high priority" tone="red" />
          <Metric icon={CircleDollarSign} label="Payment warnings" value="2" detail="Review by 17:00" tone="amber" />
          <Metric icon={Users} label="Active users" value="1,284" detail="+6.8% this month" tone="green" />
        </div>
        <div className="dashboard-grid">
          <section className="panel table-panel">
            <PanelHeader title="Latest Film Lab applications" action="Review all" onAction={() => onNavigate("approvals")} />
            <ApprovalTable compact />
          </section>
          <section className="attention-panel">
            <div className="attention-copy"><p className="eyebrow">Moderation</p><h2>Resolve high-priority reports first</h2><p>Two marketplace reports have been waiting for more than one hour.</p><button className="primary-button" onClick={() => onNavigate("moderation")}><ShieldCheck size={17} /> Open queue</button></div>
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
        <div><p className="eyebrow">Thursday workload</p><h2>Good afternoon, Khanh</h2><p>Five orders are active and one scan delivery is due today.</p></div>
        <button className="primary-button" onClick={() => onNavigate("orders")}><Boxes size={17} /> Review new orders</button>
      </section>
      <div className="metric-grid">
        <Metric icon={Boxes} label="New orders" value="6" detail="+2 since yesterday" tone="teal" />
        <Metric icon={Clock3} label="Due today" value="4" detail="1 needs attention" tone="amber" />
        <Metric icon={FileImage} label="Ready to publish" value="12" detail="38 scan files" tone="green" />
        <Metric icon={CircleDollarSign} label="September revenue" value="18.6M" detail="VND, +8.4%" tone="red" />
      </div>
      <div className="dashboard-grid">
        <section className="panel table-panel">
          <PanelHeader title="Orders in progress" action="View all" onAction={() => onNavigate("orders")} />
          <div className="table-wrap">
            <table>
              <thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Due</th><th><span className="sr-only">Open</span></th></tr></thead>
              <tbody>
                {active.slice(0, 5).map((order) => (
                  <tr key={order.id} onClick={() => { onSelect(order); onNavigate("orders"); }}>
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
          <div className="visual-caption"><span className="eyebrow">Scan room</span><strong>12 rolls ready for scanning</strong><button onClick={() => onNavigate("scans")}>Open scan delivery <ChevronRight size={15} /></button></div>
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
              {filtered.map((order) => <tr key={order.id} className={selected?.id === order.id ? "selected-row" : ""} onClick={() => onSelect(order)}><td><strong>{order.id}</strong><small>{order.service}</small></td><td>{order.customer}</td><td>{order.rolls}</td><td><StatusBadge status={order.status} /></td><td>{order.due}</td></tr>)}
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

function ScanDelivery({ onNotify }: { onNotify: (message: string) => void }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [files, setFiles] = useState<File[]>([]);
  const [progress, setProgress] = useState(0);
  const selectFiles = (event: ChangeEvent<HTMLInputElement>) => { setFiles(Array.from(event.target.files ?? [])); setProgress(0); };
  const upload = () => {
    if (!files.length) { inputRef.current?.click(); return; }
    setProgress(18);
    const timer = window.setInterval(() => setProgress((value) => {
      const next = Math.min(100, value + 22);
      if (next === 100) { window.clearInterval(timer); onNotify(`${files.length} scan file${files.length > 1 ? "s" : ""} ready to publish`); }
      return next;
    }), 260);
  };
  return <div className="two-column-layout"><section className="panel upload-panel"><div className="section-heading compact"><div><p className="eyebrow">Order FL-2036</p><h2>Upload scan files</h2></div><StatusBadge status="Quality check" /></div><button className="drop-zone" onClick={() => inputRef.current?.click()}><UploadCloud size={30} /><strong>Select JPEG or TIFF scans</strong><span>Maximum 50 MB per file</span></button><input ref={inputRef} className="sr-only" type="file" accept="image/jpeg,image/tiff" multiple onChange={selectFiles} />{files.length > 0 && <div className="file-list">{files.map((file) => <div key={`${file.name}-${file.size}`}><FileImage size={17} /><span><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(2)} MB</small></span><Check size={17} className={progress === 100 ? "success-icon" : "muted-icon"} /></div>)}<div className="progress-track"><span style={{ width: `${progress}%` }} /></div></div>}<button className="primary-button" onClick={upload}><UploadCloud size={17} /> {progress === 100 ? "Publish scans" : "Upload files"}</button></section><section className="process-summary"><h2>Delivery checklist</h2><CheckRow checked={files.length > 0} text="File type and size checked" /><CheckRow checked={progress === 100} text="Upload completed" /><CheckRow checked={false} text="Thumbnail quality reviewed" /><CheckRow checked={false} text="Customer release confirmed" /><div className="metadata-sample"><span>Scanner</span><strong>Noritsu HS-1800</strong><span>Output</span><strong>TIFF, 4,800 x 3,200</strong></div></section></div>;
}

function CheckRow({ checked, text }: { checked: boolean; text: string }) {
  return <div className={`check-row ${checked ? "is-checked" : ""}`}><span>{checked && <Check size={14} />}</span>{text}</div>;
}

function ServicesPage({ onNotify }: { onNotify: (message: string) => void }) {
  const services = [
    ["C-41 Develop", "35mm, 120", "95,000 VND", "2 days", "Active"],
    ["Develop + JPEG Scan", "35mm", "155,000 VND", "3 days", "Active"],
    ["Develop + TIFF Scan", "35mm, 120", "230,000 VND", "4 days", "Active"],
    ["B&W Hand Develop", "35mm, 120", "210,000 VND", "5 days", "Paused"],
  ];
  return <section className="panel table-panel"><div className="toolbar"><label className="search-field"><Search size={17} /><input placeholder="Search services" aria-label="Search services" /></label><button className="primary-button" onClick={() => onNotify("New service form opened")}><CircleDollarSign size={17} /> Add service</button></div><div className="table-wrap"><table><thead><tr><th>Service</th><th>Formats</th><th>Starting price</th><th>Turnaround</th><th>Status</th></tr></thead><tbody>{services.map((service) => <tr key={service[0]}><td><strong>{service[0]}</strong></td><td>{service[1]}</td><td>{service[2]}</td><td>{service[3]}</td><td><StatusBadge status={service[4]} /></td></tr>)}</tbody></table></div></section>;
}

function CustomersPage({ role }: { role: PortalRole }) {
  const people = role === "lab" ? [["Minh Anh", "8 orders", "1,860,000 VND", "Active"], ["Gia Huy", "5 orders", "920,000 VND", "Active"], ["Thu Trang", "11 orders", "3,240,000 VND", "VIP"], ["Quoc Bao", "3 orders", "720,000 VND", "Active"]] : [["Nguyen Minh Anh", "Photographer", "Sep 10, 2026", "Active"], ["Silver Grain Lab", "Lab owner", "Sep 10, 2026", "Pending"], ["Le Gia Huy", "Moderator", "Sep 9, 2026", "Active"], ["Tran Thu Trang", "Photographer", "Sep 8, 2026", "Suspended"]];
  return <section className="panel table-panel"><div className="toolbar"><label className="search-field"><Search size={17} /><input aria-label="Search people" placeholder={role === "lab" ? "Search customers" : "Search users or roles"} /></label><button className="secondary-button"><ListFilter size={17} /> Filters</button></div><div className="table-wrap"><table><thead><tr><th>{role === "lab" ? "Customer" : "User"}</th><th>{role === "lab" ? "Orders" : "Role"}</th><th>{role === "lab" ? "Lifetime value" : "Last activity"}</th><th>Status</th></tr></thead><tbody>{people.map((person) => <tr key={person[0]}><td><strong>{person[0]}</strong></td><td>{person[1]}</td><td>{person[2]}</td><td><StatusBadge status={person[3]} /></td></tr>)}</tbody></table></div></section>;
}

function ReportsPage({ role }: { role: PortalRole }) {
  const bars = [42, 57, 48, 71, 64, 82, 76];
  return <div className="reports-layout"><section className="panel chart-panel"><div className="section-heading compact"><div><p className="eyebrow">Last 7 days</p><h2>{role === "lab" ? "Completed orders" : "Platform activity"}</h2></div><button className="secondary-button"><Filter size={16} /> This week</button></div><div className="bar-chart" aria-label="Seven day activity chart">{bars.map((height, index) => <div key={index}><span style={{ height: `${height}%` }} /><small>{["Fri", "Sat", "Sun", "Mon", "Tue", "Wed", "Thu"][index]}</small></div>)}</div></section><section className="report-summary"><h2>Summary</h2><dl className="detail-list"><div><dt>Completed</dt><dd>{role === "lab" ? "34 orders" : "1,492 actions"}</dd></div><div><dt>Average time</dt><dd>{role === "lab" ? "2.8 days" : "1.2 sec"}</dd></div><div><dt>Customer rating</dt><dd>4.8 / 5.0</dd></div><div><dt>Change</dt><dd className="positive">+8.4%</dd></div></dl></section></div>;
}

function ApprovalsPage({ onNotify }: { onNotify: (message: string) => void }) {
  return <section className="panel table-panel"><div className="toolbar"><label className="search-field"><Search size={17} /><input aria-label="Search applications" placeholder="Search application or Film Lab" /></label><button className="secondary-button"><Filter size={17} /> Pending review</button></div><ApprovalTable onNotify={onNotify} /></section>;
}

function ApprovalTable({ compact = false, onNotify }: { compact?: boolean; onNotify?: (message: string) => void }) {
  return <div className="table-wrap"><table><thead><tr><th>Application</th><th>Location</th><th>Submitted</th><th>Complete</th>{!compact && <th>Action</th>}</tr></thead><tbody>{approvalQueue.map((application) => <tr key={application.id}><td><strong>{application.name}</strong><small>{application.id}</small></td><td>{application.city}</td><td>{application.submitted}</td><td><div className="completion"><span><i style={{ width: `${application.completeness}%` }} /></span>{application.completeness}%</div></td>{!compact && <td><button className="table-action" onClick={() => onNotify?.(`${application.name} opened for review`)}>Review <ChevronRight size={15} /></button></td>}</tr>)}</tbody></table></div>;
}

function ModerationPage({ onNotify }: { onNotify: (message: string) => void }) {
  const [resolved, setResolved] = useState<string[]>([]);
  return <section className="moderation-list">{reports.map((report) => <article className={`moderation-item ${resolved.includes(report.id) ? "is-resolved" : ""}`} key={report.id}><span className={`priority ${report.priority.toLowerCase()}`}>{report.priority}</span><div><strong>{report.subject}</strong><p>{report.type} · {report.id} · {report.age} ago</p></div><div className="item-actions"><button className="secondary-button" onClick={() => onNotify(`${report.id} evidence opened`)}>View evidence</button><button className="primary-button" disabled={resolved.includes(report.id)} onClick={() => { setResolved((items) => [...items, report.id]); onNotify(`${report.id} resolved and added to audit log`); }}><Check size={16} /> {resolved.includes(report.id) ? "Resolved" : "Resolve"}</button></div></article>)}</section>;
}

function MarketplacePage({ onNotify }: { onNotify: (message: string) => void }) {
  return <><div className="toolbar marketplace-toolbar"><label className="search-field"><Search size={17} /><input aria-label="Search listings" placeholder="Search listing, seller, or ID" /></label><button className="secondary-button"><Filter size={17} /> All listings</button></div><section className="listing-grid">{listings.map((listing, index) => <article className="listing-card" key={listing.id}><div className={`listing-image crop-${index}`}><img src="/images/analog-workspace.png" alt="Film photography equipment listing" /><span><StatusBadge status={listing.status} /></span></div><div className="listing-body"><small>{listing.category} · {listing.id}</small><h2>{listing.title}</h2><strong>{listing.price}</strong><p>Seller: {listing.seller}</p><button className="secondary-button full-button" onClick={() => onNotify(`${listing.id} opened for moderation`)}><ClipboardCheck size={16} /> Review listing</button></div></article>)}</section></>;
}

function ArchivePage() {
  const archiveItems = ["Da Lat morning", "Saigon after rain", "Coastal walk", "Old neighborhood", "Studio test roll", "Weekend photowalk"];
  return <><div className="toolbar"><label className="search-field"><Search size={17} /><input aria-label="Search archive" placeholder="Search album, film stock, or tag" /></label><button className="secondary-button"><Filter size={17} /> Private archive</button></div><section className="archive-grid">{archiveItems.map((item, index) => <article className={`archive-card crop-${index % 3}`} key={item}><img src="/images/analog-workspace.png" alt="Preview from analog film archive" /><div><strong>{item}</strong><small>Portra 400 · {12 + index * 4} scans</small></div></article>)}</section></>;
}

function SettingsPage({ onNotify }: { onNotify: (message: string) => void }) {
  return <form className="settings-form" onSubmit={(event) => { event.preventDefault(); onNotify("Portal settings saved"); }}><section><h2>Portal preferences</h2><label>Display name<input defaultValue="Saigon Grain Lab" /></label><label>Notification email<input type="email" defaultValue="operations@example.com" /></label><label>Default processing time<select defaultValue="3"><option value="2">2 business days</option><option value="3">3 business days</option><option value="5">5 business days</option></select></label></section><section><h2>Notifications</h2><Toggle label="New customer orders" checked /><Toggle label="Orders approaching deadline" checked /><Toggle label="Weekly performance report" checked={false} /></section><button className="primary-button" type="submit"><Check size={17} /> Save settings</button></form>;
}

function Toggle({ label, checked }: { label: string; checked: boolean }) {
  return <label className="toggle-row"><span>{label}</span><input type="checkbox" defaultChecked={checked} /><i aria-hidden="true" /></label>;
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
