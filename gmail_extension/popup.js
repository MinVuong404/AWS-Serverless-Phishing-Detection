const API_URL = "https://p7ailap9ci.execute-api.ap-southeast-1.amazonaws.com/predict";

document.addEventListener('DOMContentLoaded', () => {
  const btnTest = document.getElementById('btnQuickTest');
  const txtInput = document.getElementById('testInput');
  const resultDiv = document.getElementById('testResult');

  btnTest.addEventListener('click', async () => {
    const text = txtInput.value.trim();
    if (!text) {
      alert('Vui lòng nhập nội dung cần kiểm tra.');
      return;
    }

    btnTest.disabled = true;
    btnTest.innerText = 'Đang kiểm tra...';
    resultDiv.style.display = 'none';

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      resultDiv.style.display = 'block';

      const score = data.confidence * 100;

      if (score >= 75) {
        resultDiv.className = 'test-result result-phishing';
        resultDiv.innerHTML = `
          <strong>Cảnh báo: Phát hiện dấu hiệu lừa đảo nguy hiểm</strong><br>
          - Mức độ rủi ro: ${score.toFixed(1)}%<br>
          - Thời gian phản hồi: ${data.latency_ms} ms
        `;
      } else if (score >= 50) {
        resultDiv.className = 'test-result result-warning';
        resultDiv.innerHTML = `
          <strong>Lưu ý: Thư có tính chất quảng cáo hoặc tiếp thị</strong><br>
          - Mức độ rủi ro tiềm ẩn: ${score.toFixed(1)}%<br>
          - Thời gian phản hồi: ${data.latency_ms} ms
        `;
      } else {
        resultDiv.className = 'test-result result-safe';
        resultDiv.innerHTML = `
          <strong>Xác nhận: Văn bản an toàn / hợp lệ</strong><br>
          - Độ tin cậy an toàn: ${(100 - score).toFixed(1)}%<br>
          - Thời gian phản hồi: ${data.latency_ms} ms
        `;
      }
    } catch (err) {
      resultDiv.style.display = 'block';
      resultDiv.className = 'test-result result-phishing';
      resultDiv.innerText = `Lỗi kết nối: ${err.message}`;
    } finally {
      btnTest.disabled = false;
      btnTest.innerText = 'Kiểm tra văn bản';
    }
  });
});
