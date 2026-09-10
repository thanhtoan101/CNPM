export type OrderStatus =
  | "New"
  | "Film received"
  | "Developing"
  | "Scanning"
  | "Quality check"
  | "Completed";

export type Order = {
  id: string;
  customer: string;
  service: string;
  rolls: number;
  status: OrderStatus;
  due: string;
  price: string;
  note?: string;
};

export const orders: Order[] = [
  {
    id: "FL-2048",
    customer: "Minh Anh",
    service: "Develop + Scan XL",
    rolls: 2,
    status: "New",
    due: "Today, 17:30",
    price: "360,000 VND",
    note: "Keep the film borders in the final scans.",
  },
  {
    id: "FL-2046",
    customer: "Gia Huy",
    service: "C-41 Develop",
    rolls: 1,
    status: "Film received",
    due: "Tomorrow, 10:00",
    price: "95,000 VND",
  },
  {
    id: "FL-2042",
    customer: "Thu Trang",
    service: "Develop + TIFF Scan",
    rolls: 3,
    status: "Developing",
    due: "Sep 12, 15:00",
    price: "690,000 VND",
  },
  {
    id: "FL-2039",
    customer: "Quoc Bao",
    service: "B&W Develop + Scan",
    rolls: 2,
    status: "Scanning",
    due: "Sep 12, 18:00",
    price: "420,000 VND",
  },
  {
    id: "FL-2036",
    customer: "Thanh Lam",
    service: "120 Develop + Scan",
    rolls: 1,
    status: "Quality check",
    due: "Today, 16:00",
    price: "245,000 VND",
  },
  {
    id: "FL-2028",
    customer: "Anh Khoa",
    service: "Develop + JPEG Scan",
    rolls: 2,
    status: "Completed",
    due: "Sep 9, 11:00",
    price: "310,000 VND",
  },
];

export const approvalQueue = [
  { id: "LAB-118", name: "Silver Grain Lab", city: "Ho Chi Minh City", submitted: "18 min ago", completeness: 92 },
  { id: "LAB-117", name: "Light Meter Studio", city: "Da Nang", submitted: "2 hours ago", completeness: 78 },
  { id: "LAB-114", name: "Hanoi Film Room", city: "Ha Noi", submitted: "Yesterday", completeness: 100 },
];

export const reports = [
  { id: "RP-081", type: "Marketplace listing", subject: "Unverified Leica M6 listing", priority: "High", age: "12 min" },
  { id: "RP-079", type: "Community comment", subject: "Personal information in comment", priority: "Medium", age: "48 min" },
  { id: "RP-074", type: "Seller dispute", subject: "Item condition differs from listing", priority: "High", age: "3 hr" },
];

export const listings = [
  { id: "MK-240", title: "35mm rangefinder body", category: "Camera", price: "8,900,000 VND", seller: "Long Nguyen", status: "Active" },
  { id: "MK-237", title: "50mm manual focus lens", category: "Lens", price: "2,450,000 VND", seller: "Mai Linh", status: "Reserved" },
  { id: "MK-229", title: "Fresh color film bundle", category: "Film", price: "520,000 VND", seller: "Analog Corner", status: "Active" },
];

