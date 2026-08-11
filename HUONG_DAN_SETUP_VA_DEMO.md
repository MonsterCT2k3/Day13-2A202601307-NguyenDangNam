# HƯỚNG DẪN SETUP MÔI TRƯỜNG & KỊCH BẢN DEMO CHI TIẾT
**Dự án:** Day 13 — AI System Observability Lab (FastAPI, Streamlit, Langfuse, PII Redaction)  
**Tác giả / Sinh viên:** Nguyễn Đăng Nam  

---

## PHẦN 1: SETUP MÔI TRƯỜNG TỪ ĐẦU (WINDOWS POWERSHELL)

Nếu máy bạn vừa clone project về và chưa có môi trường Python, hãy thực hiện các bước sau:

### Bước 1: Mở PowerShell tại thư mục dự án
Đảm bảo bạn đang đứng ở thư mục gốc:
```powershell
cd d:\AITHUCCHIEN\day13\Day13-2A202601307-NguyenDangNam
```

### Bước 2: Tạo và kích hoạt môi trường ảo Python (`.venv`)
```powershell
# 1. Cho phép PowerShell chạy script (nếu bị chặn ExecutionPolicy)
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 2. Tạo virtual environment
python -m venv .venv

# 3. Kích hoạt virtual environment
.\.venv\Scripts\Activate.ps1
```
*(Khi kích hoạt thành công, đầu dòng lệnh sẽ có tiền tố `(.venv)` màu xanh).*

### Bước 3: Cài đặt toàn bộ thư viện cần thiết
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Bước 4: Tạo file cấu hình môi trường `.env`
```powershell
Copy-Item .env.example .env
```
*(Nếu có tài khoản Langfuse, bạn có thể mở file `.env` và dán `LANGFUSE_PUBLIC_KEY` & `LANGFUSE_SECRET_KEY`. Nếu không có key, app vẫn tự động chạy chế độ Mock/Local an toàn).*

---

## PHẦN 2: CÁCH KHỞI ĐỘNG HỆ THỐNG (MỞ 2 TERMINAL)

Để demo trực quan, bạn cần mở **2 cửa sổ Terminal** (nhớ kích hoạt `.venv` ở cả 2 terminal):

### 🖥️ Terminal 1: Khởi động API Backend (FastAPI)
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```
* **Địa chỉ API:** `http://localhost:8000`
* **Swagger Docs UI:** `http://localhost:8000/docs`
* **Health check:** `http://localhost:8000/health`

### 📊 Terminal 2: Khởi động Web Dashboard UI (Streamlit)
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run dashboard.py
```
* Trình duyệt sẽ tự động mở giao diện Dashboard tại: `http://localhost:8501`.

---

## PHẦN 3: KỊCH BẢN DEMO CHI TIẾT (LUỒNG CHẤM BÀI 100 ĐIỂM)

Bạn mở thêm **Terminal 3** để gõ các lệnh điều khiển, load test và trình chiếu kết quả trên trình duyệt.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌────────────────────────┐
│  1. METRICS     │  ──>  │  2. TRACES      │  ──>  │  3. LOGS        │  ──>  │  4. ROOT CAUSE & FIX   │
│  P95 Latency Đỏ │       │  Span RAG Chậm  │       │  Correlation ID │       │  Tắt Incident / Cache  │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └────────────────────────┘
```

---

### 🟢 MÀN 1: DEMO TRẠNG THÁI BÌNH THƯỜNG (BASELINE)

1. **Thao tác (Terminal 3):** Gửi tải request bình thường:
   ```powershell
   python scripts/load_test.py
   ```
2. **Trình diễn trên Dashboard (`http://localhost:8501`):**
   * Bấm nút **🔄 Refresh Now** (hoặc để Auto Refresh).
   * **Lời thoại giải thích:**
     > *"Thưa thầy/cô, hệ thống hiện đang ở trạng thái Baseline bình thường:*
     > - *Panel 1 (Latency): P95 đạt ~130ms, nhỏ hơn ngưỡng SLO 2000ms (Huy hiệu xanh **PASS**).*
     > - *Panel 2 (Traffic): Lưu lượng phân bổ đều đặn.*
     > - *Panel 3 (Errors): Tỷ lệ lỗi 0%.*
     > - *Panel 4 & 5: Cost và Token nằm trong hạn mức an toàn.*
     > - *Panel 6: Điểm chất lượng Quality Proxy trung bình đạt >0.75."*

---

### 🔒 MÀN 2: DEMO LOGGING, CORRELATION ID & CHE DỮ LIỆU NHẠY CẢM (PII)

1. **Thao tác (Terminal 3):** Chạy script kiểm tra chuẩn hoá log và lọc PII:
   ```powershell
   python scripts/validate_logs.py
   ```
2. **Kết quả hiển thị:** Điểm tuyệt đối **100/100**.
3. **Lời thoại giải thích:**
   > *"Hệ thống đã triển khai JSON Logging có cấu trúc chặt chẽ:*
   > - *Mỗi request được gán một `correlation_id` duy nhất xuyên suốt toàn bộ các tầng dịch vụ.*
   > - *Cơ chế PII Redaction tự động phát hiện và che giấu toàn bộ Email, Số điện thoại Việt Nam, CCCD và Thẻ tín dụng thành `[REDACTED_EMAIL]`, `[REDACTED_PHONE]`, `[REDACTED_CARD]` trước khi ghi xuống file `data/logs.jsonl`."*

---

### 🚨 MÀN 3: KÍCH HOẠT SỰ CỐ & ĐIỀU TRA INCIDENT (TRỌNG TÂM)

1. **Thao tác (Terminal 3):** Bơm sự cố nghẽn mạng RAG vào hệ thống và bắn tải:
   ```powershell
   # 1. Kích hoạt sự cố RAG Slow
   python scripts/inject_incident.py --scenario rag_slow

   # 2. Gửi tải để hệ thống ghi nhận sự cố
   python scripts/load_test.py
   ```

2. **Quy trình điều tra 4 bước để trình bày:**

#### Bước 3.1: Nhận diện bất thường từ Metrics (Dashboard UI)
* Mở Dashboard (`http://localhost:8501`), chỉ vào Panel 1:
* **Lời thoại:**
  > *"Quan sát Panel 1 (Latency Percentiles), chỉ số P95 Latency tăng vọt lên **2516ms**, vi phạm ngưỡng SLO cho phép (≤ 2000ms), bảng điều khiển lập tức cảnh báo màu đỏ **`[ALERT / THRESHOLD BREACH]`**."*

#### Bước 3.2: Khoanh vùng lỗi bằng Traces Waterfall
* Mở ảnh bằng chứng: `submission/evidence/trace_waterfall.png` (hoặc mở Langfuse UI).
* **Lời thoại:**
  > *"Chúng ta mở Trace Waterfall của request lỗi (ví dụ `req-4d436cfd`). Tổng thời gian xử lý là 2516.4ms, trong đó span `retrieve` của module RAG chiếm tới **2500ms** (>95% tổng thời gian). Điều này chứng minh nút thắt cổ chai (bottleneck) nằm tại bước tra cứu tri thức RAG."*

#### Bước 3.3: Đối chiếu bằng chứng từ Logs
* Mở file `data/logs.jsonl` (hoặc báo cáo `submission/REPORT.md`).
* **Lời thoại:**
  > *"Sử dụng `correlation_id: req-4d436cfd`, log ghi nhận sự kiện `event: response_sent` với `latency_ms: 2516.4` khớp chính xác với trace span."*

#### Bước 3.4: Kết luận Nguyên nhân gốc & Giải pháp khắc phục
* **Nguyên nhân gốc (Root Cause):** Incident `rag_slow` kích hoạt làm hàm `retrieve()` trong `app/mock_rag.py` bị trễ 2.5s mỗi khi tra cứu kiến thức cho tính năng hoàn tiền (`refund`).
* **Giải pháp khắc phục tức thời (Fix Action):**
  Tắt incident:
  ```powershell
  python scripts/inject_incident.py --disable rag_slow
  ```
  *(Trong hệ thống production: tối ưu lại Vector Index database, thêm tầng In-memory Caching như Redis).*
* **Giải pháp phòng ngừa dài hạn (Preventive Measure):**
  - Đặt hard timeout cho RAG span (ví dụ tối đa 1000ms).
  - Cấu hình Circuit Breaker và Fallback Response khi RAG database bị quá tải để không làm treo luồng chat của người dùng.

---

### 🏷️ MÀN 4: DEMO PROMPT VERSIONING & ROLLBACK

1. **Lời thoại giải thích:**
   > *"Hệ thống quản lý Prompt theo các phiên bản độc lập:*
   > - *`v1`: Prompt cơ bản chạy môi trường `production`.*
   > - *`v2`: Prompt nâng cao chạy thử nghiệm môi trường `staging`.*
   > - *Toàn bộ trace gửi đi đều được gắn nhãn `prompt_name`, `prompt_version`, `prompt_label` cho phép A/B testing và Rollback về phiên bản cũ ngay lập tức nếu phiên bản mới làm tăng latency hoặc giảm quality score."*

---

## PHẦN 4: BẢNG TỔNG HỢP CÁC LỆNH NHANH (CHEAT SHEET)

| Mục đích | Lệnh thực thi (PowerShell) |
|---|---|
| Kích hoạt môi trường | `.\.venv\Scripts\Activate.ps1` |
| Chạy API Server | `uvicorn app.main:app --reload` |
| Chạy Dashboard UI | `streamlit run dashboard.py` |
| Bắn tải thường | `python scripts/load_test.py` |
| Bơm sự cố RAG Slow | `python scripts/inject_incident.py --scenario rag_slow` |
| Tắt sự cố RAG Slow | `python scripts/inject_incident.py --disable rag_slow` |
| Chấm điểm Log & PII | `python scripts/validate_logs.py` |
| Kiểm tra Dashboard Contract | `python scripts/validate_dashboard.py` |
| Chạy Unit Test | `python -m pytest -q` |
