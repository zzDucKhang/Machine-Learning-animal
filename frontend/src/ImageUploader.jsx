import React, { useState } from "react";

export default function ImageUploader({ onPredict }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);

  // Dán ảnh từ clipboard
  const handlePaste = (e) => {
    const items = e.clipboardData.items;
    for (let item of items) {
      if (item.type.indexOf("image") !== -1) {
        const imgFile = item.getAsFile();
        const url = URL.createObjectURL(imgFile);
        setPreview(url);
        setFile(imgFile);
      }
    }
  };

  // Upload ảnh từ máy
  const handleFileUpload = (e) => {
    const imgFile = e.target.files[0];
    if (!imgFile) return;
    const url = URL.createObjectURL(imgFile);
    setPreview(url);
    setFile(imgFile);
  };

  // Kéo thả ảnh
  const handleDrop = (e) => {
    e.preventDefault();
    const imgFile = e.dataTransfer.files[0];
    if (!imgFile) return;
    const url = URL.createObjectURL(imgFile);
    setPreview(url);
    setFile(imgFile);
  };

  const handleDragOver = (e) => e.preventDefault();

  // Gửi ảnh lên API khi bấm nút
  const handlePredictClick = () => {
    if (file && onPredict) {
      onPredict(file);
    } else {
      alert("Vui lòng chọn hoặc dán ảnh trước!");
    }
  };

  // Xóa ảnh nhưng giữ nguyên mọi thứ khác
  const handleClearClick = () => {
    setFile(null);
    setPreview(null);
  };

  return (
    <div
      tabIndex={0}
      onPaste={handlePaste}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      style={{
        border: "2px dashed #888",
        borderRadius: 10,
        padding: 20,
        textAlign: "center",
      }}
    >
      <h3>Dán ảnh (Ctrl + V), kéo thả hoặc chọn ảnh</h3>

      <input
        type="file"
        accept="image/*"
        onChange={handleFileUpload}
        style={{ marginTop: 10 }}
      />

      {preview && (
        <div style={{ marginTop: 20 }}>
          <img
            src={preview}
            alt="preview"
            width="300"
            style={{ borderRadius: 10 }}
          />
        </div>
      )}

      <div style={{ marginTop: 20 }}>
        <button
          onClick={handlePredictClick}
          style={{
            padding: "10px 20px",
            fontSize: 16,
            borderRadius: 5,
            cursor: "pointer",
            marginRight: 10,
          }}
        >
          Predict
        </button>

        {preview && (
          <button
            onClick={handleClearClick}
            style={{
              padding: "10px 20px",
              fontSize: 16,
              borderRadius: 5,
              cursor: "pointer",
              backgroundColor: "#f44336",
              color: "#fff",
              border: "none",
            }}
          >
            Xóa ảnh
          </button>
        )}
      </div>
    </div>
  );
}
