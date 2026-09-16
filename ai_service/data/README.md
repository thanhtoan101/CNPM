# Dữ liệu mẫu của AI Service

- `film_labs.json` chứa **Film Lab, giá, rating và lượt review hoàn toàn giả
  lập** để kiểm thử phần mềm. Không dùng các bản ghi này để đưa ra quyết định
  dịch vụ thật.
- `knowledge_base.json` là nội dung minh họa do dự án biên soạn, chưa phải tài
  liệu đã được chuyên gia duyệt. Các URI `kb://` là mã nguồn nội bộ để truy vết,
  không phải liên kết công khai.
- `evaluation_cases.json` là bộ relevance fixture nhỏ, tổng hợp. Kết quả trên
  bộ này chỉ chứng minh pipeline và metric chạy tái lập; không phải độ chính xác
  production.

Trước production, nhóm phải thay dữ liệu mẫu bằng dữ liệu có quyền sử dụng,
version, nguồn, người duyệt, ngày duyệt và quy trình kiểm soát thay đổi.
