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

      if (data.status === "error") {
        throw new Error(data.message || "Processing failed");
      }

      // Create data URL from base64
      const src = `data:image/png;base64,${data.base64_image}`;
      setImageUrl(src);
    } catch (error) {
      console.error("Error:", error);
      alert(`Something went wrong: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>Character Art Generator</h1>
      <p style={{ color: "#666", marginBottom: "2rem" }}>
        Upload an image and convert it to art made entirely of the letter 'a'
      </p>

      <div style={{ marginBottom: "2rem" }}>
        <input
          type="file"
          accept="image/*"
          onChange={(e) => {
            if (e.target.files?.[0]) {
              setFile(e.target.files[0]);
              setImageUrl(null);
            }
          }}
          style={{
            padding: "0.5rem",
            border: "2px solid #ddd",
            borderRadius: "4px",
          }}
        />
      </div>

      <button
        onClick={handleUpload}
        disabled={!file || loading}
        style={{
          padding: "0.75rem 1.5rem",
          fontSize: "1rem",
          backgroundColor: !file || loading ? "#ccc" : "#007bff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: !file || loading ? "not-allowed" : "pointer",
          fontWeight: "bold",
        }}
      >
        {loading ? "Processing... (this may take a minute)" : "Generate Character Art"}
      </button>

      {loading && (
        <div style={{ marginTop: "1rem", color: "#666" }}>
          <p>⏳ Converting your image to character art...</p>
          <p style={{ fontSize: "0.9rem" }}>
            This process analyzes each tile and finds the best rotation of 'a' to match it.
          </p>
        </div>
      )}

      {imageUrl && (
        <div style={{ marginTop: "2rem" }}>
          <h3>Character Art Result:</h3>
          <p style={{ color: "#666", fontSize: "0.9rem", marginBottom: "1rem" }}>
            Your image recreated using only the letter 'a' at different rotations!
          </p>
          <img
            src={imageUrl}
            alt="Character art result"
            style={{
              maxWidth: "100%",
              height: "auto",
              border: "1px solid #ddd",
              borderRadius: "8px",
              boxShadow: "0 4px 8px rgba(0,0,0,0.1)",
            }}
          />
          <div style={{ marginTop: "1rem" }}>
            <a
              href={imageUrl}
              download="character-art.png"
              style={{
                display: "inline-block",
                padding: "0.5rem 1rem",
                backgroundColor: "#28a745",
                color: "white",
                textDecoration: "none",
                borderRadius: "4px",
                fontWeight: "bold",
              }}
            >
              Download Image
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;