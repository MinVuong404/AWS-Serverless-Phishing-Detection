/**
 * Background Service Worker
 * Chịu trách nhiệm thực hiện các yêu cầu mạng (fetch) đến AWS API Gateway.
 * Vượt qua 100% rào cản Content Security Policy (CSP) và CORS của trang Gmail.
 */

const DEFAULT_API_URL = "https://p7ailap9ci.execute-api.ap-southeast-1.amazonaws.com/predict";

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "PREDICT_PHISHING") {
    console.log("[Background] Đang gửi yêu cầu phân tích tới AWS API Gateway...");
    console.log("[Background] Nội dung text:", request.text);

    // Lấy API URL từ storage nếu có, hoặc dùng mặc định
    chrome.storage.sync.get(['apiEndpoint'], (result) => {
      const targetUrl = result.apiEndpoint || DEFAULT_API_URL;

      fetch(targetUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          text: request.text
        })
      })
      .then(async (response) => {
        if (!response.ok) {
          const errorBody = await response.text();
          console.error("[Background] API trả về lỗi HTTP:", response.status, errorBody);
          sendResponse({
            success: false,
            error: `Máy chủ AWS trả về HTTP ${response.status}: ${errorBody}`
          });
        } else {
          const data = await response.json();
          console.log("[Background] Phản hồi thành công từ AWS:", data);
          sendResponse({
            success: true,
            data: data
          });
        }
      })
      .catch((err) => {
        console.error("[Background] Lỗi mạng khi gọi AWS:", err);
        sendResponse({
          success: false,
          error: `Không thể kết nối đến AWS: ${err.message}`
        });
      });
    });

    // Bắt buộc return true để cho phép sendResponse hoạt động bất đồng bộ (asynchronous)
    return true;
  }
});
