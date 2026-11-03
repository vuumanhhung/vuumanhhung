# Cài thống kê ngôn ngữ public + private cho @vuumanhhung

## 1. Tạo Fine-grained Personal Access Token

Trên GitHub mở: Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token.

- Resource owner: **vuumanhhung**
- Repository access: **All repositories** (để gồm cả private repo hiện tại và về sau)
- Repository permissions: **Metadata — Read-only** (mặc định; không cần quyền đọc Contents)
- Chọn thời hạn token; hết hạn thì phải cập nhật secret.

GitHub REST API `GET /user/repos` và `GET /repos/{owner}/{repo}/languages` chỉ cần Metadata (read). Chức năng này xem dữ liệu GitHub đã nhận diện, không tải source code về.

## 2. Lưu token vào GitHub Actions Secrets

Trong repo `https://github.com/vuumanhhung/vuumanhhung`:

Settings > Secrets and variables > Actions > New repository secret

- Name: `PROFILE_STATS_TOKEN`
- Value: token vừa tạo.

**Đừng đưa token vào README, code, file .yml, issue hoặc chat.**

## 3. Đưa file lên profile repository

Giải nén ZIP và đưa ba đường dẫn sau vào repo `vuumanhhung/vuumanhhung` (giữ nguyên cấu trúc):

- `README.md`
- `scripts/update_languages.py`
- `.github/workflows/update-languages.yml`

Nếu repo hiện có README, nhớ sao lưu hoặc gộp nội dung trước khi thay.

## 4. Chạy lần đầu

Actions > **Update language statistics (public + private)** > Run workflow.

Nếu bước commit báo lỗi 403, vào Settings > Actions > General > Workflow permissions, chọn **Read and write permissions**, rồi chạy lại.

Workflow sẽ chạy thủ công khi yêu cầu hoặc vào mỗi thứ Hai; chỉ commit khi bảng thay đổi.

## Dữ liệu nào được hiển thị?

- Gộp ngôn ngữ GitHub Linguist nhận ra từ các repo **do vuumanhhung sở hữu**, public lẫn private.
- Không tính fork hay repo profile; không tính repo của người khác nơi bạn chỉ là collaborator.
- Hiện tên ngôn ngữ, phần trăm dung lượng code và tổng số ngôn ngữ; không hiện danh sách/tên private repo, số byte tuyệt đối hay source code.
- HTML/CSS cũng được tính nếu GitHub Linguist liệt kê, vì mục tiêu là hiển thị **tất cả ngôn ngữ GitHub nhận diện**.
- Tỉ lệ theo số byte, **không phản ánh mức độ thành thạo**. Tính cả code thư viện/vendor nếu GitHub Linguist thống kê chúng.
- Số liệu tổng hợp vẫn công khai gián tiếp rằng bạn có dùng các ngôn ngữ ấy trong dự án riêng tư.

Nếu không thấy private repo, kiểm tra token có chọn **All repositories**, thuộc đúng tài khoản và chưa hết hạn. Nếu là private repo của tổ chức, có thể cần token cấp bởi tổ chức hoặc một cấu hình riêng.

Nếu muốn ngừng thống kê private, xóa secret và thu hồi token ở GitHub Settings; dữ liệu đã commit lên README vẫn công khai cho đến khi thay đổi hoặc xóa khỏi lịch sử commit.
