# AI-powered Film Photography Platform

Đồ án CNPM: kết nối người chụp ảnh film với Film Lab, quản lý xử lý/giao scan, kho ảnh, marketplace và trợ lý nhiếp ảnh.

## Bắt đầu xem bài

- [Báo cáo PDF](docs/CNPM_Report.pdf) và [nguồn LaTeX](CNPM_Report.tex).
- [Yêu cầu chức năng: 6 luồng, 9 module](docs/FunctionalRequirements.md).
- [Thiết kế Mobile/Web, sơ đồ Mermaid](docs/MobileWeb.md).
- [User stories, business rules, ma trận truy vết](docs/AcceptanceTraceability.md).
- [Kết quả kiểm thử và giới hạn](docs/Verification.md).
- [Checklist và kịch bản demo](docs/SubmissionChecklist.md).

## Phạm vi đã có

| Thành phần | Có thể thực hiện | Ranh giới |
| --- | --- | --- |
| React/TypeScript | Dịch vụ, tìm/lọc đơn, chuyển công đoạn, kiểm tra scan, duyệt Lab, moderation, archive metadata, CSV; lưu state trình duyệt | Dữ liệu demo; chưa nối API/cloud; chuyển portal không phải phân quyền |
| Flutter | Tìm Lab, booking preview, orders, archive, marketplace, AI trả lời mẫu | Chưa kiểm thử thiết bị; chưa đồng bộ backend |
| Express/PostgreSQL | JWT, GET/POST cơ bản, quyền quản trị, giới hạn đơn theo chủ sở hữu, giá đơn phía server | Test dùng DB stub; cần PostgreSQL thật để kiểm thử tích hợp |
| Python AI | Recommendation theo ràng buộc, retrieval, trả lời có nguồn, heuristic chất lượng scan | Dữ liệu cục bộ; chưa phải GPT/cloud đã triển khai |
| Deployment | Docker, Azure templates, workflow CI | Chưa xác minh deployment đang hoạt động |

## Chạy Web (Node.js 24 LTS)

```sh
cd apps/web
npm ci
npm test
npm run build
npm run dev
```

Mở `http://127.0.0.1:4173`. Thay đổi lưu trong localStorage của trình duyệt; dùng dữ liệu mẫu. [Hướng dẫn frontend/mobile](apps/README.md).

## Chạy AI (Python 3.11+)

```sh
python -m pip install .
python -m unittest discover -s tests -v
python -m ai_service.api
```

AI chạy tại `http://127.0.0.1:8080`, hợp đồng `/openapi.json`. Backend: đọc [backend/README.md](backend/README.md), cấu hình `.env`, bootstrap DB phát triển mới bằng `schema.sql`, rồi `npm ci`, `npm test`, `npm start` trong `backend/`. Không commit `.env` hoặc khóa bí mật.

## Báo cáo và nhóm

Chạy `tectonic CNPM_Report.tex` hoặc XeLaTeX hai lần từ thư mục gốc. Dùng Unicode engine để giữ tên tiếng Việt, không dùng pdfLaTeX.

| Thành viên | Phần chính |
| --- | --- |
| Nguyễn Thái Gia Bảo | Bối cảnh, yêu cầu nghiệp vụ |
| Lê Thị Như Quân | Kiến trúc, cơ sở dữ liệu |
| Huỳnh Gia Hợp | Backend/API |
| Nguyễn Đào Quốc Khánh | Yêu cầu chức năng, Mobile/Web |
| Nguyễn Thành Toàn | AI, kiểm thử, triển khai |

Nội dung Khánh trước đây ở nhánh riêng đã được tích hợp qua [PR #8](https://github.com/thanhtoan101/CNPM/pull/8) và [PR #9](https://github.com/thanhtoan101/CNPM/pull/9). Lịch sử commit, nội dung và bằng chứng Jira xác định đóng góp; chiều cao cột commit không đo chất lượng.
