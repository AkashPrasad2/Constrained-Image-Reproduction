import { useState } from "react";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();

      // Create data URL from base64 (so <img> can use it directly)
      const src = `data:image/png;base64,${data.base64_image}`;
      setImageUrl(src);
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong :(");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif" }}>
      <h1>Upload your image</h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            setFile(e.target.files[0]);
            setImageUrl(null); // clear previous result when new file is selected
          }
        }}
      />

      <br />
      <br />

      <button onClick={handleUpload} disabled={!file || loading}>
        {loading ? "Processing..." : "Upload & Convert to Grayscale"}
      </button>

      {/* Show the result image when we have it */}
      {imageUrl && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Grayscale result:</h3>
          <img
            src={imageUrl}
            alt="Grayscale result"
            style={{
              maxWidth: "100%",
              maxHeight: "600px",
              border: "1px solid #ddd",
              borderRadius: "8px",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            }}
          />
        </div>
      )}
    </div>
  );
}

export default App;