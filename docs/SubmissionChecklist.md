# Checklist nộp bài và demo CNPM — phần Khánh

Checklist nội bộ ngày 17/09/2026, hỗ trợ chuẩn bị bài nộp và trình bày. Không thay thế yêu cầu chính thức của giảng viên. Chỉ đánh dấu mục đã thực hiện và có bằng chứng tương ứng.

Kết quả thực tế của lần rà soát nằm trong [Verification.md](Verification.md): 61 kiểm thử tự động đạt, web build đạt, kiểm tra Services lưu sau reload đạt, PDF 38 trang đã xem. Các ca thủ công bên dưới giữ trạng thái chưa chạy nếu chưa thực hiện trọn kịch bản; unit test không thay thế kết quả chạy thiết bị hoặc tích hợp.

## 1. Kiểm tra gói nộp

- [ ] Đối chiếu lại đề/rubric và nơi nộp chính thức; xác nhận tên file, hình thức nộp, hạn nộp và người nộp của nhóm.
- [ ] Nhánh dùng nộp đã chứa phần FunctionalRequirements và MobileWeb; mở đường dẫn từ tài khoản khác/ẩn danh nếu người chấm cần quyền truy cập.
- [x] `docs/FunctionalRequirements.md` chứa đủ 6 Core Flows, AI assistance và Main Functional Modules; không còn chỉ là các tiêu đề trống.
- [x] `docs/AcceptanceTraceability.md` phân biệt đặc tả, prototype và kiểm chứng; có user stories, business rules, actors và liên kết kiểm tra.
- [x] Biên dịch `CNPM_Report.tex`, mở PDF vừa tạo, kiểm tra mục lục, tên/thành viên, hình/sơ đồ, bảng, ngắt trang và liên kết.
- [x] Báo cáo chứa phần Khánh và thể hiện đúng mức hoàn thiện của sản phẩm; không mô tả dữ liệu mẫu thành số liệu chạy thật.
- [ ] Hướng dẫn chạy trong `README.md`/`apps/README.md` khớp các lệnh và cổng thực tế của bản nộp.
- [ ] Lưu bằng chứng lệnh build/test và commit được chạy; lỗi chưa xử lý phải được nêu rõ.
- [ ] Các việc Jira của Khánh có link commit/file/PR phù hợp; link xem được và nội dung đã có trên nhánh được chỉ rõ.
- [ ] Nếu cần một bản nộp chính thức, nhóm tự kiểm tra và thực hiện bước nộp sau cùng; chưa coi việc push GitHub là đã nộp lên hệ thống môn học.

## 2. Kịch bản demo khoảng 6 phút

| Thời lượng | Thao tác | Điểm cần giải thích |
| --- | --- | --- |
| 0:00–0:40 | Mở sơ đồ UI flow và danh sách vai trò trong MobileWeb. | Photographer dùng Flutter; nhân viên Lab và Admin dùng web. Chỉ rõ phạm vi phần Khánh. |
| 0:40–1:40 | Film Lab → Orders: tìm một đơn, lọc trạng thái, mở chi tiết. | Mã đơn, số cuộn, dịch vụ, ghi chú và trạng thái; dữ liệu hiện là dữ liệu demo. |
| 1:40–2:30 | Chuyển một đơn sang bước tiếp theo, mở Processing board. | Chuỗi trạng thái hợp lệ; không tuyên bố mobile nhận cập nhật thật nếu chưa có kiểm chứng tích hợp. |
| 2:30–3:20 | Scan delivery: chọn tệp mẫu hợp lệ, trình bày kiểm tra và bước công bố. | Tách giao diện/tiến độ demo với upload thật đến cloud; nêu rõ kết quả đã kiểm tra ở bản cuối. |
| 3:20–4:10 | Admin → Lab approvals/Moderation, xem thông tin và thao tác đã có. | Phê duyệt/moderation là luồng khác với quyền truy cập. Nút chuyển vai trò chỉ phục vụ demo. |
| 4:10–5:20 | Nếu Flutter chạy được: Home → Lab → booking preview → Orders → Archive/Market. | Đây là các prototype UI; không gọi toast tạo bản nháp là một đơn được lưu thật. Nếu chưa chạy được, trình bày thiết kế và ghi rõ mobile chưa được kiểm chứng runtime. |
| 5:20–6:00 | Mở ma trận truy vết và bằng chứng build/test của đúng commit. | Chỉ ra phần hoàn thành, giới hạn và các tích hợp còn lại; không đọc toàn bộ bảng màn hình. |

Chuẩn bị sẵn một tệp JPEG nhỏ dùng cho demo và một tệp sai định dạng cho kiểm tra âm. Không dùng ảnh cá nhân hoặc dữ liệu thật của khách hàng. Bản demo nên bắt đầu bằng tải lại ứng dụng để biết rõ dữ liệu nào được khởi tạo và dữ liệu nào được lưu bền vững.

## 3. Bộ kiểm tra thủ công có thể lặp lại

Các mục dưới đây là **kế hoạch kiểm tra, chưa ghi nhận kết quả chạy**. “Kỳ vọng” là điều cần quan sát hoặc tiêu chí cần đánh giá, không phải cam kết mọi chức năng đã cài đặt.

| ID | Bước thực hiện | Kỳ vọng / bằng chứng cần lưu | Trạng thái ban đầu |
| --- | --- | --- | --- |
| TC-W01 | Mở web, chuyển Film Lab/Admin, vào các trang menu rồi Settings. | Tên trang/menu đúng vai trò; điều hướng không lỗi. Ghi rõ đây là role switch của demo, không phải kiểm tra RBAC. | Chưa chạy |
| TC-W02 | Orders: tìm theo mã/khách; kết hợp trạng thái; nhập chuỗi chắc chắn không khớp rồi xóa bộ lọc. | Dòng khớp chính xác; có trạng thái rỗng; phục hồi danh sách khi xóa lọc; chi tiết tương ứng đúng đơn. | Chưa chạy |
| TC-W03 | Chọn đơn chưa hoàn tất, chuyển từng bước; kiểm tra Orders và Processing board; thử tại Completed. | Hai màn hình web phản ánh cùng trạng thái; không có bước tiếp sau Completed; ghi rõ dữ liệu có/không tồn tại sau reload. | Chưa chạy |
| TC-W04 | Scan delivery: chọn JPEG/TIFF hợp lệ; thử tệp sai định dạng, tệp quá giới hạn, bỏ chọn; chạy xử lý và bước công bố. | Tệp không hợp lệ không được coi đã kiểm tra; kiểm tra kiểm soát công bố/xác nhận; không tuyên bố upload cloud khi chỉ có tiến độ mô phỏng. Ghi kết quả âm nếu chưa đạt. | Chưa chạy |
| TC-W05 | Admin: xem một hồ sơ Lab và một báo cáo; thực hiện thao tác có trên màn hình, thử lặp và reload. | Phân biệt xem chi tiết, phản hồi mẫu và quyết định được lưu; báo cáo đã xử lý không bị xử lý lặp trong phiên; audit/persistence chỉ ghi đạt nếu đã chứng minh. | Chưa chạy |
| TC-W06 | Mở Services, Customers/Users, Marketplace, Archive; thử từng tìm kiếm/bộ lọc đang hiển thị. | Ghi rõ điều khiển nào thay dữ liệu thật và điều khiển nào chỉ là giao diện mẫu; không đánh dấu đạt chỉ vì ô nhập tồn tại. | Chưa chạy |
| TC-W07 | Thu cửa sổ web xuống khoảng 390 px; mở/đóng menu, vào bảng đơn và scan; dùng Tab để đi qua điều khiển. | Không che mất thao tác chính; bảng có thể cuộn; focus nhìn thấy; lưu ảnh/mô tả lỗi nếu có. | Chưa chạy |
| TC-M01 | Flutter Home: tìm theo tên/quận; đổi 35mm/120/B&W; nhập từ khóa không có kết quả. | Danh sách mẫu phản ánh cả từ khóa và định dạng; có thông báo không tìm thấy. | Chưa chạy |
| TC-M02 | Mở Lab details; đổi dịch vụ/số cuộn; thử giảm dưới 1; chọn Book service. | Số cuộn hợp lệ; đối chiếu giá theo dịch vụ; chỉ mô tả tạo đơn thật khi đơn được lưu và xuất hiện trong Orders. Nếu chỉ có phản hồi mẫu, ghi “booking preview”. | Chưa chạy |
| TC-M03 | Orders: chuyển Active/Completed, mở một đơn và timeline. | Nhóm/trạng thái đúng dữ liệu mẫu; các mốc hiển thị rõ; không suy ra đồng bộ với web từ timeline tĩnh. | Chưa chạy |
| TC-M04 | Archive: mở album, thử Create/Download; Market: lọc danh mục, mở chi tiết và Save draft. | Ghi từng hành vi: dialog/preview, thay đổi dữ liệu hay toast; chỉ ghi download/lưu đạt khi có tệp/bản ghi thực tế. | Chưa chạy |
| TC-M05 | AI Assistant: câu trống, câu có nội dung; Profile: đổi tùy chọn. | Câu trống bị chặn; nhận biết câu trả lời demo; xác nhận phạm vi lưu của tùy chọn, không suy ra thay đổi tài khoản thật. | Chưa chạy |
| TC-D01 | Mở báo cáo PDF và các link từ AcceptanceTraceability/MobileWeb. | Phần yêu cầu không trống; sơ đồ và danh mục prototype khớp nguồn; đủ thông tin để giải thích 6 luồng và giới hạn hiện tại. | Chưa chạy |

Mẫu ghi kết quả cho mỗi lần chạy:

```text
Commit / branch:
Ngày giờ, người chạy:
Máy / hệ điều hành / trình duyệt hoặc thiết bị:
ID kiểm tra:
Bước thực hiện và dữ liệu:
Kết quả quan sát:
Đạt / Không đạt / Bị chặn / Không áp dụng:
Bằng chứng (log, ảnh hoặc file):
Lỗi / việc Jira liên quan:
```

## 4. Kiểm tra tự động và giới hạn bằng chứng

Chạy lệnh theo hướng dẫn phiên bản hiện tại của [apps/README.md](../apps/README.md). Ghi nguyên lệnh và kết quả vào báo cáo kiểm thử của bản nộp.

- Web: kiểm tra lệnh được khai báo trong `apps/web/package.json`, chạy build và bộ test có trong bản nộp. Build thành công chứng minh khả năng biên dịch; chưa thay thế các kiểm tra workflow ở trên.
- Mobile: `flutter analyze` và `flutter test` khi đã có Flutter SDK/phụ thuộc phù hợp. Tệp `apps/mobile/test/widget_test.dart` hiện có smoke test cho tên ứng dụng, nội dung Home và 5 đích điều hướng; test này không bao phủ booking, upload, marketplace hay API.
- Nếu không có Flutter SDK hoặc thiết bị, ghi **Bị chặn: thiếu môi trường Flutter**. Không ghi “Pass” từ việc chỉ đọc mã Dart.
- Kết quả test của dịch vụ AI/backend phải có phạm vi riêng; không dùng chúng để thay thế kiểm tra tích hợp giữa frontend và API.

## 5. Cập nhật Jira và đóng gói bằng chứng

| Nhóm việc | Bằng chứng nên đính kèm khi đã kiểm tra |
| --- | --- |
| SCRUM-4/5/6/8/9/10 | Link `docs/FunctionalRequirements.md` của commit cuối, vị trí flow tương ứng và trạng thái đã vào nhánh dùng nộp hay chưa. |
| SCRUM-26/27 | Link MobileWeb, AcceptanceTraceability, hướng dẫn chạy và ảnh/bằng chứng responsive thực tế nếu đã chụp. |
| SCRUM-28 | Các tệp Flutter, phạm vi prototype, kết quả analyze/test hoặc lý do chưa chạy. |
| SCRUM-29/30/31 | Màn hình và tương tác web đã thực hiện, lệnh build/test, kết quả các TC-W liên quan và giới hạn backend. |
| SCRUM-32 | UI/component/sequence trong MobileWeb, phần báo cáo, danh mục màn hình prototype và ghi chú demo. Không ghi đã có bộ wireframe độc lập nếu chưa tạo. |
| SCRUM-22 | Dùng ma trận truy vết để rà soát phạm vi tổng; giữ nguyên phân công/trạng thái cho đến khi người phụ trách xác nhận. |

Chỉ mô tả công việc và kết quả có thật. Commit nên tương ứng với thay đổi có ý nghĩa; không tạo commit rỗng hoặc sửa ngày để tăng biểu đồ đóng góp. Đảm bảo email tác giả đúng tài khoản GitHub và nội dung được đưa vào nhánh mặc định theo quy trình nhóm để bằng chứng đóng góp dễ kiểm tra.
