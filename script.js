// Webcam access
const video = document.getElementById('video');
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => { video.srcObject = stream; })
  .catch(err => { console.error("❌ Webcam error:", err); });

const captureBtn = document.getElementById('captureBtn');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const liveResult = document.getElementById('liveResult');

captureBtn.addEventListener('click', () => {
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL('image/jpeg');

  fetch('/upload_live_image', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ image: imageData })
  })
  .then(response => response.json())
  .then(data => {
    liveResult.innerHTML = `
      <h2>🧾 Live Prediction Result</h2>
      <p><strong>Status:</strong> ${data.prediction}</p>
      <p><strong>Confidence:</strong> ${(data.confidence * 100).toFixed(2)}%</p>
    `;
  })
  .catch(err => {
    console.error("❌ Upload failed:", err);
  });
});
