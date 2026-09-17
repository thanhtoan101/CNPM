# Đối chiếu yêu cầu và bằng chứng nghiệm thu — phần Khánh

Ngày rà soát: 17/09/2026. Phạm vi: tài liệu yêu cầu chức năng và thiết kế/prototype Mobile–Web của Nguyễn Đào Quốc Khánh.

Tài liệu này đối chiếu nội dung đang có trong kho mã với các việc Jira SCRUM-4, SCRUM-5, SCRUM-6, SCRUM-8, SCRUM-9, SCRUM-10 và SCRUM-26 đến SCRUM-32. SCRUM-22 đến SCRUM-25 được dùng để đối chiếu nội dung Context/Proposed Solutions/Functional Requirements; tài liệu không thay đổi người phụ trách hoặc trạng thái các việc đó. Đây là tiêu chí nội bộ suy ra từ yêu cầu dự án, không phải rubric của giảng viên.

## 1. Cách đọc mức hoàn thành

- **Đặc tả:** hành vi mong muốn đã được mô tả trong tài liệu. Chưa có nghĩa là đã cài đặt.
- **Prototype:** đã có màn hình hoặc tương tác với dữ liệu mẫu trong mã frontend. Chưa có nghĩa là API, phân quyền, lưu trữ và đồng bộ đã được tích hợp.
- **Đã kiểm chứng:** chỉ sử dụng khi có lệnh/bước chạy, kết quả, môi trường và commit tương ứng trong bằng chứng kiểm thử.

Ma trận dưới đối chiếu tài liệu với mã nguồn bản cuối. Kết quả chạy thực tế (9 web unit tests, 11 backend tests, 41 AI tests và kiểm tra Chrome có giới hạn) nằm riêng trong [Verification.md](Verification.md). Danh sách kiểm tra thủ công nằm trong [SubmissionChecklist.md](SubmissionChecklist.md).

Nguồn chính: [FunctionalRequirements.md](FunctionalRequirements.md), [MobileWeb.md](MobileWeb.md), [phần yêu cầu trong báo cáo](../sections/03-functional-requirements.tex), [phần thiết kế Mobile–Web](../sections/10-mobile-web-design.tex), [hướng dẫn chạy](../apps/README.md).

## 2. Tác nhân và ranh giới trách nhiệm

| Tác nhân | Mục tiêu và dữ liệu được sử dụng | Màn hình/ranh giới cần thể hiện |
| --- | --- | --- |
| Photographer / Customer | Tìm Lab, đặt dịch vụ, theo dõi đơn, nhận và tổ chức ảnh của mình | Flutter Home, Orders, Archive, Market, Profile |
| Film Lab Owner | Quản lý dịch vụ, giá, nhân viên và đơn thuộc Lab của mình | Web Film Lab; quyền chủ Lab là yêu cầu cần backend kiểm tra |
| Film Lab Employee | Tiếp nhận đơn, cập nhật công đoạn, kiểm tra và giao bản scan | Web Orders, Processing board, Scan delivery |
| Photography Expert / Community Member | Chia sẻ bài viết, trả lời thảo luận, tổ chức hoạt động | Core Flow 6; feed/đăng bài/sự kiện là phần đặc tả chưa được chứng minh bằng prototype hiện tại |
| Delivery Partner | Nhận yêu cầu lấy/giao phim và cập nhật tiến độ vận chuyển | Core Flow 2; cần tích hợp logistics |
| System Administrator / Moderator | Duyệt Lab, xử lý báo cáo, quản lý tài khoản và giám sát nền tảng | Web Admin; chuyển nút Film Lab/Admin trong demo không phải xác thực hay RBAC |
| AI Assistant / AI Service | Nhận câu hỏi/ngữ cảnh, trả lời hoặc đưa gợi ý kèm giới hạn | Flutter có giao diện hỏi đáp; câu trả lời mẫu không chứng minh đã gọi dịch vụ AI |

## 3. User stories và tiêu chí chấp nhận

Các mã US/BR/TC dưới đây là mã truy vết trong tài liệu này, không phải mã Jira mới.

| Mã | User story | Tiêu chí chấp nhận của yêu cầu | Jira |
| --- | --- | --- | --- |
| US-01 | Là Photographer, tôi muốn tìm Lab theo tên/khu vực/định dạng phim để chọn dịch vụ phù hợp. | Kết hợp từ khóa và định dạng; giữ bộ lọc khi không có kết quả; hiển thị giá, đánh giá và thời gian xử lý. | SCRUM-5, SCRUM-28 |
| US-02 | Là Photographer, tôi muốn xem dịch vụ, số cuộn và chi phí trước khi đặt. | Số cuộn ít nhất 1; giá tính theo lựa chọn; phân biệt bản xem trước với đơn đã được lưu; luồng đầy đủ có pickup/drop-off và xác nhận của Lab. | SCRUM-6, SCRUM-28 |
| US-03 | Là nhân viên Lab, tôi muốn tìm và xem một đơn để xử lý đúng khách hàng. | Lọc từ khóa và trạng thái; chi tiết hiển thị đúng mã đơn, dịch vụ, số cuộn, ghi chú và trạng thái. | SCRUM-8, SCRUM-29 |
| US-04 | Là nhân viên Lab, tôi muốn chuyển đơn sang công đoạn hợp lệ và để khách theo dõi. | Chỉ chuyển bước kế tiếp hợp lệ; đơn hoàn tất không tiến thêm; luồng tích hợp lưu người thao tác/thời gian và đồng bộ đến khách. | SCRUM-8, SCRUM-29 |
| US-05 | Là nhân viên Lab, tôi muốn kiểm tra rồi công bố scan đúng đơn. | Kiểm tra loại/kích thước tệp; tách chọn tệp, xử lý và công bố; công bố có xác nhận; giao thật cần storage và quyền truy cập. | SCRUM-9, SCRUM-29 |
| US-06 | Là Photographer, tôi muốn xem và quản lý ảnh của mình. | Xem album/metadata; thao tác tổ chức không sửa tệp gốc; chỉ người được phép mới truy cập ảnh riêng tư. | SCRUM-9, SCRUM-31 |
| US-07 | Là thành viên cộng đồng, tôi muốn tìm tin thiết bị và xem trạng thái trước khi liên hệ. | Hiển thị danh mục/giá/người bán/trạng thái; trạng thái không sẵn có không được tạo giao dịch mới; giao dịch thật cần lưu và theo dõi. | SCRUM-10, SCRUM-31 |
| US-08 | Là Moderator, tôi muốn xem thông tin vụ việc và ghi quyết định xử lý. | Có ngữ cảnh báo cáo, quyết định và lý do; không xử lý lặp; nghiệp vụ đầy đủ cần audit log lưu phía server. | SCRUM-30 |
| US-09 | Là quản trị viên, tôi muốn xem hồ sơ Lab trước khi duyệt. | Hiển thị độ đầy đủ/thông tin hồ sơ; yêu cầu bổ sung hoặc từ chối có lý do; ghi quyết định và thông báo. | SCRUM-30 |
| US-10 | Là người dùng, tôi muốn nhận phản hồi rõ ràng khi tải dữ liệu hoặc thao tác thất bại. | Có trạng thái rỗng/lỗi/đang xử lý; nhãn không chỉ dựa vào màu; bố cục dùng được ở màn hình hẹp. | SCRUM-27 |
| US-11 | Là Photographer, tôi muốn hiểu giới hạn của AI khi hỏi về nhiếp ảnh. | Không gửi câu hỏi trống; phân biệt trả lời mẫu với trả lời từ AI; khi tích hợp cần nguồn/giới hạn và phương án khi dịch vụ lỗi. | SCRUM-28; nội dung AI trong SCRUM-22/25 |
| US-12 | Là người xem báo cáo, tôi muốn theo dõi một yêu cầu từ luồng nghiệp vụ tới màn hình và cách kiểm tra. | Có liên kết nguồn, sơ đồ UI/component/sequence, minh họa màn hình và trạng thái thực hiện rõ ràng. | SCRUM-4, SCRUM-26, SCRUM-32 |

## 4. Quy tắc nghiệp vụ

| Mã | Quy tắc và căn cứ | Phạm vi đã có / còn cần tích hợp |
| --- | --- | --- |
| BR-01 | Lab chỉ xử lý dữ liệu thuộc Lab của mình; vai trò chủ Lab được quản lý giá/nhân viên. Nguồn: MobileWeb §3. | Yêu cầu phân quyền. Nút đổi portal trong prototype chỉ chọn giao diện; cần kiểm tra quyền tại API. |
| BR-02 | Số cuộn phải là số nguyên dương và chi phí phải rõ trước khi xác nhận. Nguồn: FunctionalRequirements Core Flow 2; MobileWeb §2. | Mobile có bộ tăng/giảm số cuộn và ước tính. Cần kiểm tra giá theo từng dịch vụ và lưu đơn/collection thật. |
| BR-03 | Tiến độ xử lý phải tuân thủ thứ tự; bất thường/độ trễ phải được ghi nhận. Nguồn: Core Flow 3; MobileWeb §3. | Web có chuyển trạng thái cục bộ theo chuỗi. Washing/drying/image preparation là nghiệp vụ chi tiết; demo gom các bước, chưa chứng minh đồng bộ mobile. |
| BR-04 | Scan gắn đúng đơn/khách, tệp lỗi không được giao, công bố sau kiểm tra chất lượng. Nguồn: Core Flow 4; MobileWeb §3. | Màn hình chọn/xử lý tệp là prototype. Upload đến cloud, kiểm tra quyền và thông báo giao thật cần tích hợp. |
| BR-05 | Scan mới mặc định riêng tư; thay tag/album không ghi đè bản gốc. Nguồn: MobileWeb §6. | Nhãn/quy tắc giao diện đã mô tả; bảo vệ file phải được kiểm tra ở storage/API. |
| BR-06 | Tin đã bán/đặt trước/hết hạn/bị ẩn không mở giao dịch mới. Nguồn: Core Flow 5; MobileWeb §5. | Có nhãn trạng thái mẫu. Backend marketplace/giao dịch và kiểm thử quy tắc còn cần bằng chứng riêng. |
| BR-07 | Duyệt/từ chối Lab và xử lý nội dung cần lý do, xác nhận phù hợp và audit log. Nguồn: MobileWeb §4. | Có hàng đợi và tương tác demo; thông báo thành công không tự chứng minh audit log đã được lưu. |
| BR-08 | Hủy/đổi sự kiện phải thông báo; đủ chỗ thì đóng đăng ký hoặc dùng danh sách chờ. Nguồn: Core Flow 6. | Đã đặc tả; chưa có luồng sự kiện hoạt động trong frontend hiện tại. |
| BR-09 | AI phải nêu giới hạn khi thiếu thông tin; tìm kiếm thường vẫn dùng được khi AI lỗi. Nguồn: FunctionalRequirements phần AI. | Đã đặc tả. UI mobile dùng câu trả lời mẫu; đánh giá dịch vụ AI thuộc phạm vi tích hợp riêng. |
| BR-10 | Dữ liệu mẫu không phải số liệu kinh doanh hoặc kết quả benchmark. Nguồn: apps/README và các tệp demo_data/data. | Áp dụng khi trình bày dashboard, doanh thu, số người dùng và tốc độ trên màn hình demo. |

## 5. Ma trận yêu cầu → màn hình → kiểm tra

| Yêu cầu / quy tắc | Đường dẫn và màn hình hiện có | Bằng chứng từ mã nguồn | Kiểm tra liên quan |
| --- | --- | --- | --- |
| US-01, BR-09 | `apps/mobile/lib/screens/home_screen.dart` — Home, Film Lab details | Tìm Lab theo tên/địa điểm và lọc định dạng trên danh sách mẫu; có trạng thái rỗng. Xếp hạng AI/map chưa được nối dịch vụ. | TC-M01 |
| US-02, BR-02 | Cùng tệp — Lab details / booking preview | Chọn dịch vụ/số cuộn, xem ước tính và phản hồi khi đặt; chưa chứng minh tạo đơn ở backend. | TC-M02 |
| US-03 | `apps/web/src/App.tsx` — OrdersPage, OrderDetail | Tìm đơn, lọc trạng thái và hiển thị chi tiết trên dữ liệu frontend. | TC-W02 |
| US-04, BR-03 | Cùng tệp — ProcessingBoard; `apps/mobile/lib/screens/orders_screen.dart` | Web chuyển bước trong state; mobile hiển thị timeline từ dữ liệu mẫu riêng. Chưa phải luồng đồng bộ giữa hai ứng dụng. | TC-W03, TC-M03 |
| US-05, BR-04 | `apps/web/src/FeaturePages.tsx` — ScanDelivery; `domain.ts` | Kiểm tra loại/MIME/kích thước/số tệp/trùng tên, kiểm duyệt rồi công bố metadata riêng tư; có unit test. File picker chưa kiểm chứng do extension chặn; chưa upload cloud. | TC-W04 |
| US-06, BR-05 | `apps/mobile/lib/screens/archive_screen.dart`; web ArchivePage | Có danh sách/chi tiết album và giao diện archive; download, lưu metadata và bảo vệ file cần kiểm chứng riêng. | TC-M04, TC-W06 |
| US-07, BR-06 | `apps/mobile/lib/screens/marketplace_screen.dart`; web MarketplacePage | Danh sách thiết bị, nhãn trạng thái; mobile lọc danh mục và mở chi tiết/form bản nháp. Không phải giao dịch thương mại đã hoàn tất. | TC-M04, TC-W06 |
| US-08, BR-07 | `apps/web/src/FeaturePages.tsx` — ModerationPage; `domain.ts`, `DemoStore.tsx` | Lý do quyết định, chặn xử lý lặp, ẩn tin liên quan, audit và localStorage; unit test đạt. Chưa có audit server/phân quyền thật. | TC-W05 |
| US-09, BR-07 | Cùng tệp — ApprovalsPage, ApprovalTable | Xem hồ sơ, chặn duyệt hồ sơ thiếu, yêu cầu lý do khi từ chối/bổ sung, audit cục bộ; logic có unit test. Chưa gửi thông báo/backend. | TC-W05 |
| US-10 | `apps/web/src/styles.css`, App Sidebar; `apps/mobile/lib/theme/app_theme.dart` | Có responsive layout, nhãn trạng thái, empty state và theme dùng chung. Chưa có kết quả đánh giá accessibility toàn diện. | TC-W01, TC-W07 |
| US-11, BR-09 | `apps/mobile/lib/screens/home_screen.dart` — AssistantSheet | Giao diện hỏi đáp và chặn câu trống; câu trả lời mẫu không chứng minh RAG hoặc mô hình thật. | TC-M05 |
| US-12 | `docs/MobileWeb.md` §7–10; `sections/10-mobile-web-design.tex` | UI/component/sequence bằng Mermaid và danh mục màn hình prototype; không có bộ wireframe độc lập được khẳng định. | TC-D01 |

## 6. Cách gắn bằng chứng GitHub và Jira

1. Dùng commit/PR chứa nội dung thực tế và đường dẫn file; ghi rõ nhánh nếu chưa vào nhánh mặc định.
2. Liên kết kết quả kiểm thử với commit đã chạy. Không lấy lần build cũ để chứng minh thay đổi mới.
3. SCRUM-4/5/6/8/9/10 được nghiệm thu theo **tài liệu**; SCRUM-27–32 được nghiệm thu theo **thiết kế** đã mô tả. Phần prototype cần nêu các tương tác và giới hạn riêng.
4. Chỉ chuyển việc triển khai sang Done khi các tiêu chí của chính việc đó có bằng chứng. Không suy ra toàn bộ hệ thống đã hoạt động từ việc giao diện hoặc tài liệu được đánh dấu Done.
5. Trước khi đóng SCRUM-22, đối chiếu Context, Proposed Solutions, roles, business rules, six flows, user stories và traceability. Việc phân công hiện tại cần được giữ nguyên cho đến khi người phụ trách dự án xác nhận.
