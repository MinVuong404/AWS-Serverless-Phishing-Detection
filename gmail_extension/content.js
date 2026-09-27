/**
 * Gmail Phishing Detector - Content Script
 * Thiết kế giao diện phẳng (Flat Material), chuyên nghiệp, đồng bộ với chuẩn thiết kế của Gmail.
 * KHÔNG dùng icon/emoji, KHÔNG đổ bóng nổi hạt, loại bỏ hoàn toàn cảm giác công cụ AI đồ chơi.
 */

/**
 * Trích xuất và chuẩn hóa nội dung email (Lấy text thuần túy, loại bỏ hoàn toàn xuống dòng và khoảng cách thừa)
 */
function extractEmailData(messageElement) {
  // 1. Vùng chứa nội dung thư (Body container)
  const bodyEl = messageElement.querySelector('div.a3s.aiL') || 
                 messageElement.querySelector('div.ii.gt') || 
                 messageElement;

  // Lấy text thuần túy của nội dung bức thư (loại bỏ toàn bộ HTML tags, không lấy tiêu đề)
  const bodyText = bodyEl ? (bodyEl.innerText || bodyEl.textContent || '') : '';

  // 2. Chuẩn hóa: xóa toàn bộ ký tự xuống dòng (\r, \n), tab (\t), gom khoảng trắng thừa
  const cleanSingleLineText = bodyText
    .replace(/[\r\n\t]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  return {
    cleanText: cleanSingleLineText,
    bodyContainer: bodyEl
  };
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
}

/**
 * Hiển thị thanh thông báo bảo mật phân cấp 3 mức:
 * Mức 1 (< 50%): An toàn / Hợp lệ (Xanh)
 * Mức 2 (50% - 75%): Thư tiếp thị / Cần lưu ý (Vàng cam)
 * Mức 3 (>= 75%): Cảnh báo lừa đảo nguy hiểm (Đỏ)
 */
function renderSecurityBanner(container, result, cleanText) {
  // Xóa banner cũ nếu có
  const existingBanner = container.parentElement.querySelector('.security-banner');
  if (existingBanner) {
    existingBanner.remove();
  }

  const score = result.confidence * 100;
  const latency = result.latency_ms || 0;

  let tier = 'safe';
  let bannerTitle = '';
  let metaText = '';
  let descText = '';

  if (score >= 75) {
    // MỨC 3: NGUY HIỂM CAO (ĐỎ)
    tier = 'phishing';
    bannerTitle = 'Cảnh báo an toàn: Phát hiện dấu hiệu thư lừa đảo nguy hiểm';
    metaText = `Mức độ rủi ro: ${score.toFixed(1)}%`;
    descText = 'Hệ thống phát hiện dấu hiệu mạo danh danh tính hoặc yêu cầu thao tác khẩn cấp (dọa khóa tài khoản, trừ tiền, phạt tiền). Tuyệt đối không bấm vào liên kết hoặc cung cấp mật khẩu/mã OTP!';
  } else if (score >= 50) {
    // MỨC 2: TIẾP THỊ / NGHI VẤN / CẦN LƯU Ý (VÀNG)
    tier = 'warning';
    bannerTitle = 'Lưu ý an toàn: Thư có tính chất quảng cáo hoặc tiếp thị';
    metaText = `Mức độ rủi ro tiềm ẩn: ${score.toFixed(1)}%`;
    descText = 'Nội dung thư chứa nhiều liên kết hoặc từ khóa tiếp thị (game, khuyến mãi, sự kiện). Hãy kiểm tra kỹ địa chỉ người gửi trước khi tương tác với các đường dẫn.';
  } else {
    // MỨC 1: AN TOÀN (XANH)
    tier = 'safe';
    bannerTitle = 'Xác nhận an toàn: Thư hợp lệ';
    metaText = `Độ tin cậy an toàn: ${(100 - score).toFixed(1)}%`;
    descText = 'Nội dung email phù hợp với các thư trao đổi thông thường và không phát hiện dấu hiệu bất thường.';
  }

  const banner = document.createElement('div');
  banner.className = `security-banner banner-${tier}`;

  banner.innerHTML = `
    <div class="security-banner-header">
      <div class="security-banner-title">${bannerTitle}</div>
      <button class="security-banner-close" title="Đóng thông báo">✕</button>
    </div>
    
    <div class="security-banner-meta">
      <span>${metaText}</span>
      <span>•</span>
      <span>Thời gian xử lý: ${latency} ms</span>
    </div>

    <p class="security-banner-desc">${descText}</p>

    <!-- HỘP XEM CHI TIẾT DỮ LIỆU ĐÃ TRÍCH XUẤT VÀ GỬI ĐI -->
    <details class="security-banner-details">
      <summary>Xem nội dung trích xuất gửi lên AI (${cleanText.length} ký tự)</summary>
      <div class="payload-box">
        <div class="payload-actions">
          <button class="btn-copy-payload" type="button">Sao chép nội dung</button>
        </div>
        <div class="payload-content">${escapeHtml(cleanText)}</div>
      </div>
    </details>
  `;

  // Xử lý nút đóng
  banner.querySelector('.security-banner-close').addEventListener('click', () => {
    banner.remove();
  });

  // Xử lý nút sao chép nội dung
  const copyBtn = banner.querySelector('.btn-copy-payload');
  if (copyBtn) {
    copyBtn.addEventListener('click', (e) => {
      e.preventDefault();
      navigator.clipboard.writeText(cleanText).then(() => {
        copyBtn.innerText = 'Đã sao chép!';
        setTimeout(() => { copyBtn.innerText = 'Sao chép nội dung'; }, 2000);
      });
    });
  }

  // Chèn ngay phía trên nội dung email
  container.parentElement.insertBefore(banner, container);
}

/**
 * Xử lý khi nhấn nút Kiểm tra
 */
function handleScanEmail(button, messageElement) {
  const emailData = extractEmailData(messageElement);

  if (!emailData.cleanText || emailData.cleanText.length < 5) {
    alert("Không tìm thấy nội dung văn bản trong thư để kiểm tra.");
    return;
  }

  // In ra bảng Console F12 để kiểm tra chi tiết
  console.group("%c[Gmail Phishing Detector] Dữ liệu chuẩn bị gửi lên AWS", "color: #1a73e8; font-weight: bold; font-size: 13px;");
  console.log("Độ dài chuỗi:", emailData.cleanText.length, "ký tự");
  console.log("Nội dung body.text:", emailData.cleanText);
  console.groupEnd();

  // Trạng thái đang kiểm tra
  const originalText = "Kiểm tra thư";
  button.disabled = true;
  button.className = "security-scan-btn btn-scanning";
  button.innerText = "Đang kiểm tra...";

  // Gửi qua Background Service Worker
  chrome.runtime.sendMessage({
    action: "PREDICT_PHISHING",
    text: emailData.cleanText
  }, (response) => {
    button.disabled = false;

    if (chrome.runtime.lastError || !response || !response.success) {
      alert(`Lỗi kiểm tra an toàn:\n${response ? response.error : 'Không nhận được phản hồi từ dịch vụ'}`);
      button.className = "security-scan-btn";
      button.innerText = originalText;
      return;
    }

    const data = response.data;
    console.log("%c[Gmail Phishing Detector] Phản hồi từ AWS Lambda:", "color: #137333; font-weight: bold;", data);

    renderSecurityBanner(emailData.bodyContainer, data, emailData.cleanText);

    const score = data.confidence * 100;
    if (score >= 75) {
      button.className = "security-scan-btn btn-phishing";
      button.innerText = `Cảnh báo lừa đảo (${score.toFixed(0)}%)`;
    } else if (score >= 50) {
      button.className = "security-scan-btn btn-warning";
      button.innerText = `Thư tiếp thị / Lưu ý (${score.toFixed(0)}%)`;
    } else {
      button.className = "security-scan-btn btn-safe";
      button.innerText = `Thư an toàn (${(100 - score).toFixed(0)}%)`;
    }
  });
}

/**
 * Tạo nút kiểm tra (Giao diện phẳng, chuẩn Material Design của Google)
 */
function createScanButton(messageElement) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'security-scan-btn';
  button.innerText = 'Kiểm tra thư';

  button.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    handleScanEmail(button, messageElement);
  });

  return button;
}

/**
 * Quét DOM và CHỈ chèn duy nhất 1 nút vào bên trong email đang mở
 * KHÔNG chèn ở danh sách hộp thư đến bên ngoài (Inbox view)
 */
function injectScannerButton() {
  // 1. KIỂM TRA ĐIỀU KIỆN TIÊN QUYẾT:
  // Chỉ khi người dùng đang thực sự mở xem một email (có tiêu đề h2.hP) thì mới xử lý!
  const subjectEl = document.querySelector('h2.hP');
  if (!subjectEl) {
    // Nếu đang ở danh sách thư bên ngoài (Inbox list view), dọn dẹp nếu có nút thừa và dừng lại ngay
    document.querySelectorAll('.security-scan-btn').forEach(b => b.remove());
    return;
  }

  // 2. Xóa các nút cũ bên ngoài thanh công cụ đỉnh nếu có
  document.querySelectorAll('.ai-scan-phishing-btn, .ai-scan-phishing-btn-top').forEach(b => b.remove());

  // 3. CHỈ TÌM DUY NHẤT thẻ message `.adn.ads` (Không quét `div.h7` để tránh bị nhân đôi 2 nút)
  const messageCards = document.querySelectorAll('div.adn.ads');

  messageCards.forEach((msgEl) => {
    // Nếu trong thư này đã có nút rồi thì tuyệt đối không chèn thêm
    if (msgEl.querySelector('.security-scan-btn')) {
      return;
    }

    // Tìm thanh công cụ header của thư (bên cạnh ngày gửi / nút More)
    const headerActions = msgEl.querySelector('div.gE.iv.gt') || 
                          msgEl.querySelector('div.gH td.acX') || 
                          msgEl.querySelector('div.amn');

    if (headerActions) {
      const btn = createScanButton(msgEl);
      headerActions.prepend(btn);
    } else {
      // Fallback: Chèn ở đầu nội dung thư nếu không tìm thấy headerActions
      const bodyEl = msgEl.querySelector('div.a3s.aiL') || msgEl.querySelector('div.ii.gt');
      if (bodyEl && !msgEl.querySelector('.security-scan-btn')) {
        const btn = createScanButton(msgEl);
        bodyEl.parentElement.insertBefore(btn, bodyEl);
      }
    }
  });
}

// Lắng nghe thay đổi DOM
const observer = new MutationObserver(() => {
  injectScannerButton();
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Chạy thử lần đầu
setTimeout(injectScannerButton, 800);
