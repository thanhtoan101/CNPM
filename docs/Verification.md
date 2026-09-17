# Rà soát Document và Code — 17/09/2026

Môi trường: Windows, Node.js 24.19.0, Python bundled của Codex, Chrome profile Khánh. Bằng chứng phân biệt unit test, build và kiểm tra trực tiếp.

## Kết quả đã thực hiện

| Hạng mục | Lệnh / bước | Kết quả |
| --- | --- | --- |
| AI | `python -m unittest discover -s tests -p "test_*.py" -v` | 41/41 đạt; chạy ngoài sandbox để hai ca tạo file tạm có quyền ghi. |
| Web | `node --test --test-isolation=none apps/web/test/domain.test.ts` | 9/9 đạt: JSON persistence, trạng thái, dịch vụ, scan, công bố, duyệt Lab, moderation, CSV. |
| Backend | `node --test --test-isolation=none backend/test/auth.test.js` | 11/11 đạt với DB stub; không phải PostgreSQL thật. |
| Build | `tsc -b`, `vite build` trong `apps/web`; `node --check backend/server.js` | Đạt. |
| Chrome Services | Thêm E6 Test Service, giá 320.000 VND; reload; mở Services | Dữ liệu vẫn tồn tại. Đã sửa lỗi validator optional làm mất state khi reload và thêm regression test. |
| Chrome Admin | Chuyển Admin, xem hàng đợi và dashboard | Dữ liệu mẫu và audit count phản ánh thay đổi dịch vụ. |
| File picker scan | Chọn JPEG mẫu | Extension chặn chọn tệp; chưa ghi manual Pass. Logic scan/publication có unit test. |
| Báo cáo | Tectonic; render/xem bố cục 48 trang | Đạt, không tràn khung hoặc thiếu ký tự trong log. |
| Flutter | Đọc mã nguồn và test | Chưa chạy analyze/test/device do thiếu Flutter SDK. |
| Tích hợp/cloud | DB thật, frontend/API, Azure, payment/logistics/storage | Chưa chạy, không tuyên bố đã triển khai. |

Tổng: **61 kiểm thử tự động đạt (41 AI + 9 web + 11 backend)**. `npm test` ở từng thư mục dùng trên Node thông thường; `--test-isolation=none` tránh hạn chế tiến trình của sandbox.

## Lỗi/thiếu đã xử lý

1. 22 commit nội dung Khánh chưa vào main: tích hợp qua PR #8/#9, giữ tác giả/ngày gốc.
2. Đặc tả trên main chỉ có khung: đưa vào 6 core flows, AI assistance và 9 module.
3. Phần kiến trúc rỗng/không được include: bổ sung sơ đồ, trách nhiệm, luồng lỗi và ranh giới thiết kế.
4. Báo cáo đánh số thủ công/font không phù hợp: Unicode LaTeX, chương/mục tự động, bảng truy vết, sơ đồ quy trình.
5. Nút web chỉ toast: bổ sung dịch vụ, phê duyệt, moderation, tìm kiếm, metadata, preferences, audit và persistence cục bộ.
6. Dashboard cố định: tính chỉ số chính từ dữ liệu hiện tại.
7. Scan chưa kiểm tra: thêm JPEG/TIFF, MIME, dung lượng, số tệp, trùng tên và xác nhận; chỉ lưu metadata.
8. JWT ký/kiểm tra khác khóa: cấu hình chung, secret tối thiểu 32 ký tự, HS256 rõ ràng.
9. API users/schema mở và `/users/full` có thể trả hash: yêu cầu admin, chỉ trả trường an toàn.
10. Xem tất cả đơn/giá do client gửi: lọc đơn theo chủ sở hữu, giá lấy từ active service thuộc đúng Lab, chặn vai trò sai.
11. Thiếu schema và hướng dẫn backend: bootstrap SQL cho DB mới và `.env.example`; không sửa DB đang dùng của nhóm.
12. Mobile đổi dịch vụ nhưng giá không đổi, thông báo như tạo đơn: sửa giá demo, giới hạn 1–100 cuộn, nhãn preview.
13. Bản nguồn đóng gói bỏ `node_modules` và gitlink lồng nhau; cài thư viện theo lockfile.

## Còn thiếu để thành hệ thống hoàn chỉnh

- Chưa có rubric/đề gốc của giảng viên để xác nhận đủ điểm theo đề.
- Flutter SDK/device build; lưu booking/draft/archive thực.
- PostgreSQL thật, seed tài khoản, migration cho DB cũ; backend chưa đủ toàn bộ CRUD/vòng đời đơn.
- Frontend/API authentication, quyền Lab/staff, đồng bộ; refresh/revoke token, rate limiting, audit server.
- Cloud scan storage/download có quyền, payment, logistics, notification, backup/restore, deployment.

Giữ các mục này ở trạng thái chưa kiểm chứng/tích hợp tiếp; không dùng unit test để đóng toàn bộ Jira của nhóm.
