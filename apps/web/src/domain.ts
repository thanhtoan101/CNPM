import { orders, approvalQueue, reports, listings } from "./data.ts";
import type { Order, OrderStatus } from "./data.ts";

export const STORAGE_KEY = "filmops-demo-v1";
export const MAX_SCAN_BYTES = 50 * 1024 * 1024;
export const nextStatus: Partial<Record<OrderStatus, OrderStatus>> = {
  New: "Film received", "Film received": "Developing", Developing: "Scanning",
  Scanning: "Quality check", "Quality check": "Completed",
};
export type Service = { id: string; name: string; formats: string; price: number; days: number; status: "Active" | "Paused" };
export type ScanFile = { name: string; size: number; type: string };
export type Delivery = { id: string; orderId: string; files: ScanFile[]; publishedAt: string; private: true };
export type Application = typeof approvalQueue[number] & { status: "Pending" | "Approved" | "Needs information" | "Rejected"; reason: string };
export type Report = typeof reports[number] & { status: "Open" | "Resolved" | "Escalated"; decision: string; note: string; explanation: string; listingId?: string };
export type Audit = { id: string; at: string; actor: string; target: string; action: string; detail: string };
export type Album = { id: string; title: string; film: string; tags: string; favorite: boolean; count: number };
export type Settings = { name: string; email: string; days: string; newOrders: boolean; deadlines: boolean; weekly: boolean };
export type DemoState = {
  version: 1; orders: Order[]; services: Service[]; applications: Application[];
  reports: Report[]; listings: typeof listings; deliveries: Delivery[]; audit: Audit[];
  albums: Album[]; settings: Settings;
};

export function createDemoState(): DemoState {
  return {
    version: 1, orders: orders.map(order => ({ ...order })),
    services: [
      { id: "SVC-1", name: "C-41 Develop", formats: "35mm, 120", price: 95000, days: 2, status: "Active" },
      { id: "SVC-2", name: "Develop + JPEG Scan", formats: "35mm", price: 155000, days: 3, status: "Active" },
      { id: "SVC-3", name: "Develop + TIFF Scan", formats: "35mm, 120", price: 230000, days: 4, status: "Active" },
      { id: "SVC-4", name: "B&W Hand Develop", formats: "35mm, 120", price: 210000, days: 5, status: "Paused" },
    ],
    applications: approvalQueue.map(item => ({ ...item, status: "Pending", reason: "" })),
    reports: reports.map(item => ({ ...item, status: "Open", decision: "", note: "", explanation: "", ...(item.id === "RP-081" ? { listingId: "MK-240" } : {}) })),
    listings: listings.map(item => ({ ...item })), deliveries: [], audit: [],
    albums: ["Da Lat morning", "Saigon after rain", "Coastal walk", "Old neighborhood", "Studio test roll", "Weekend photowalk"].map((title, i) => ({ id: `ALB-${i + 1}`, title, film: "Portra 400", tags: "sample", favorite: false, count: 12 + i * 4 })),
    settings: { name: "Saigon Grain Lab", email: "operations@example.com", days: "3", newOrders: true, deadlines: true, weekly: false },
  };
}

export function isDemoState(value: unknown): value is DemoState {
  const sameShape = (item: unknown, sample: unknown): boolean => {
    if (Array.isArray(sample)) return Array.isArray(item) && (!sample.length || item.every(entry => sameShape(entry, sample[0])));
    if (sample !== null && typeof sample === "object") return item !== null && typeof item === "object" && Object.entries(sample).every(([key, field]) => {
      const actual = (item as Record<string, unknown>)[key];
      return (["note", "listingId"].includes(key) && actual === undefined) || sameShape(actual, field);
    });
    return typeof item === typeof sample && (typeof item !== "number" || Number.isFinite(item));
  };
  if (!sameShape(value, createDemoState())) return false;
  const state = value as DemoState;
  return state.version === 1 && state.orders.every(item => [...Object.keys(nextStatus), "Completed"].includes(item.status))
    && state.deliveries.every(item => sameShape(item, { id: "", orderId: "", files: [{ name: "", size: 1, type: "" }], publishedAt: "", private: true }) && item.private === true)
    && state.audit.every(item => sameShape(item, { id: "", at: "", actor: "", target: "", action: "", detail: "" }));
}

export function addAudit(state: DemoState, actor: string, target: string, action: string, detail: string): DemoState {
  return { ...state, audit: [...state.audit, { id: crypto.randomUUID(), at: new Date().toISOString(), actor, target, action, detail }] };
}
export function advanceOrder(state: DemoState, id: string): DemoState {
  const order = state.orders.find(item => item.id === id);
  if (!order || !nextStatus[order.status]) throw new Error("This order has no next processing stage.");
  if (order.status === "Quality check" && /scan/i.test(order.service) && !state.deliveries.some(item => item.orderId === id)) {
    throw new Error("Publish reviewed scan metadata in Scan delivery before completing this order.");
  }
  const status = nextStatus[order.status]!;
  return addAudit({ ...state, orders: state.orders.map(item => item.id === id ? { ...item, status } : item) }, "Film Lab (demo)", id, "Order stage updated", `${order.status} → ${status}`);
}
export function validateService(service: Omit<Service, "id">): string {
  if (!service.name.trim() || !service.formats.trim()) return "Service name and film formats are required.";
  if (!Number.isSafeInteger(service.price) || service.price <= 0 || service.price > 100000000) return "Price must be a whole number from 1 to 100,000,000 VND.";
  if (!Number.isInteger(service.days) || service.days < 1 || service.days > 60) return "Turnaround must be 1–60 days.";
  if (!["Active", "Paused"].includes(service.status)) return "Choose a valid service status.";
  return "";
}
export function saveService(state: DemoState, service: Service): DemoState {
  const error = validateService(service); if (error) throw new Error(error);
  if (state.services.some(item => item.id !== service.id && item.name.trim().toLowerCase() === service.name.trim().toLowerCase())) throw new Error("A service with this name already exists.");
  const clean = { ...service, name: service.name.trim(), formats: service.formats.trim() };
  const exists = state.services.some(item => item.id === service.id);
  return addAudit({ ...state, services: exists ? state.services.map(item => item.id === service.id ? clean : item) : [...state.services, clean] }, "Film Lab (demo)", service.id, exists ? "Service updated" : "Service created", clean.name);
}
export function validateScans(files: ScanFile[]): string[] {
  if (!files.length) return ["Select at least one scan file."];
  if (files.length > 100) return ["Select at most 100 files per delivery."];
  const seen = new Set<string>();
  return files.flatMap(file => {
    const errors: string[] = [];
    if (!/\.(jpe?g|tiff?)$/i.test(file.name) || (file.type && !["image/jpeg", "image/tiff"].includes(file.type))) errors.push(`${file.name}: only JPEG or TIFF is allowed.`);
    if (!Number.isFinite(file.size) || file.size <= 0 || file.size > MAX_SCAN_BYTES) errors.push(`${file.name}: size must be greater than zero and at most 50 MB.`);
    const key = file.name.toLowerCase();
    if (seen.has(key)) errors.push(`${file.name}: duplicate filename.`);
    seen.add(key);
    return errors;
  });
}
export function publishScans(state: DemoState, orderId: string, files: ScanFile[], reviewed: boolean, confirmed: boolean): DemoState {
  const errors = validateScans(files); if (errors.length) throw new Error(errors.join(" "));
  const order = state.orders.find(item => item.id === orderId);
  if (!order || order.status !== "Quality check" || !/scan/i.test(order.service)) throw new Error("Select a scan order at Quality check.");
  if (!reviewed || !confirmed) throw new Error("Confirm quality review and customer release first.");
  if (state.deliveries.some(item => item.orderId === orderId)) throw new Error("Scans have already been published for this order.");
  const delivery: Delivery = { id: crypto.randomUUID(), orderId, files: files.map(({ name, size, type }) => ({ name, size, type })), publishedAt: new Date().toISOString(), private: true };
  return addAudit({ ...state, deliveries: [...state.deliveries, delivery], orders: state.orders.map(item => item.id === orderId ? { ...item, status: "Completed" } : item) }, "Film Lab (demo)", orderId, "Scan metadata published", `${files.length} files; private; local demo only, no files uploaded or customer notified`);
}
export function decideApplication(state: DemoState, id: string, status: Application["status"], reason: string): DemoState {
  const application = state.applications.find(item => item.id === id);
  if (!application || !["Pending", "Needs information"].includes(application.status)) throw new Error("This application has already received a final decision.");
  if (status === "Pending") throw new Error("Choose a decision.");
  if (status === "Approved" && application.completeness < 100) throw new Error("Incomplete applications cannot be approved. Request the missing information.");
  if (status !== "Approved" && reason.trim().length < 10) throw new Error("Enter a reason of at least 10 characters.");
  return addAudit({ ...state, applications: state.applications.map(item => item.id === id ? { ...item, status, reason: reason.trim() } : item) }, "Admin (demo)", id, `Application ${status.toLowerCase()}`, reason.trim() || "Complete sample application reviewed");
}
export function moderateReport(state: DemoState, id: string, decision: string, note: string, explanation: string): DemoState {
  const report = state.reports.find(item => item.id === id);
  if (!report || report.status !== "Open") throw new Error("This report is no longer open.");
  if (!["Dismiss", "Hide listing", "Warn user", "Escalate"].includes(decision)) throw new Error("Choose a moderation decision.");
  if (note.trim().length < 10 || explanation.trim().length < 10) throw new Error("Internal note and user explanation each require at least 10 characters.");
  if (decision === "Hide listing" && !report.listingId) throw new Error("This report is not linked to a marketplace listing.");
  return addAudit({ ...state,
    reports: state.reports.map(item => item.id === id ? { ...item, status: decision === "Escalate" ? "Escalated" : "Resolved", decision, note: note.trim(), explanation: explanation.trim() } : item),
    listings: decision === "Hide listing" ? state.listings.map(item => item.id === report.listingId ? { ...item, status: "Hidden" } : item) : state.listings,
  }, "Admin (demo)", id, decision, `${note.trim()} | User explanation: ${explanation.trim()}`);
}
export const money = (value: number) => `${value.toLocaleString("en-US")} VND`;
export const orderValue = (order: Order) => Number(order.price.replace(/[^0-9]/g, ""));
export function csvCell(value: string | number): string {
  const text = String(value); const safe = /^[=+@\-\t\r]/.test(text) ? `'${text}` : text;
  return `"${safe.replaceAll('"', '""')}"`;
}
