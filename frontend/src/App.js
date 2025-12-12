import React, { useState } from "react";
import ImageUploader from "./ImageUploader";

function App() {
  const [result, setResult] = useState(null);

  const sendToAPI = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Có lỗi khi gửi ảnh lên API!");
    }
  };

  console.log({result})

  return (
    <div style={{ padding: 40 }}>
      <h1>Dự đoán hình ảnh (Dog / Cat / Bird / Human / ...)</h1>

      <ImageUploader onPredict={sendToAPI} />

      {result && (
        <div style={{ marginTop: 20 }}>
          <h2>Kết quả: <h1>{result.prediction_label}</h1> </h2>
          
          
        </div>
      )}
    </div>
  );
}

export default App;
