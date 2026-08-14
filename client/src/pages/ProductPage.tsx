import { useState } from "react";
import styles from "./ProductPage.module.css";

export default function ProductPage() {
  const [prompt, setPrompt] = useState("");
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [trained, setTrained] = useState(false);
  const [prediction, setPrediction] = useState("");
  const [model, setModel] = useState("Auto");
  const [fileName, setFileName] = useState("");
  const [csvHeaders, setCsvHeaders] = useState<string[] | null>(null);
  const [csvPreview, setCsvPreview] = useState<string[][]>([]);
  const [csvText, setCsvText] = useState<string>("");

  const trainModel = async () => {
    setTraining(true);
    setTrained(false);
    setProgress(0);

    // send CSV + metadata to backend /product
    try {
      const base = import.meta.env.VITE_SERVER_API_ROOT || "localhost:8080";

      const endpoint = base.startsWith("http")
        ? `${base}/product`
        : `http://${base}/product`;

      console.log("Sending upload request to", endpoint, {
        fileName,
        csv: csvText,
        prompt,
        model,
      });
      console.log("CSV preview:", csvText);

      // fire-and-log upload request (do not block UI progress simulation)
      fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fileName,
          csv: csvText,
          prompt,
          model,
          csvPreview,
        }),
      })
        .then(async (res) => {
          if (!res.ok) {
            const t = await res.text();
            console.error("Upload failed:", res.status, t);
          } else {
            const data = await res.json().catch(() => null);
            console.log("Upload success", data);
          }
        })
        .catch((err) => console.error("Upload error", err));
    } catch (err) {
      console.error("Failed to start upload", err);
    }

    const timer = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(timer);
          setTraining(false);
          setTrained(true);
          return 100;
        }

        return prev + 4;
      });
    }, 120);
  };

  function parseCsvLine(line: string) {
    // Split on commas that are not inside quotes
    const parts = line.split(/,(?=(?:[^"]*"[^"]*")*[^"]*$)/);
    return parts.map((p) => p.replace(/^\s*"?/, "").replace(/"?\s*$/, ""));
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".csv")) {
      alert("Please upload a CSV file");
      return;
    }
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (ev) => {
      const text = String(ev.target?.result ?? "");
      setCsvText(text);
      const rows = text.split(/\r\n|\n/).filter((r) => r.trim() !== "");
      if (rows.length === 0) {
        setCsvHeaders(null);
        setCsvPreview([]);
        return;
      }
      const parsed = rows.map((r) => parseCsvLine(r));
      setCsvHeaders(parsed[0] ?? null);
      setCsvPreview(parsed.slice(1, 6)); // preview first 5 data rows
    };
    reader.readAsText(file);
  };

  return (
    <main className={styles.page}>
      <section className={styles.hero}>
        <p className={styles.badge}>AI Model Studio</p>
        <h1>Train machine learning models from CSV files</h1>
        <p>
          Upload your dataset, describe your goal, and generate a usable model
          without writing code.
        </p>
      </section>

      <section className={styles.workspace}>
        <div className={styles.mainPanel}>
          <div className={styles.panelHeader}>
            <div>
              <h2>Build model</h2>
              <p>Step 1 of 2 · Dataset and training goal</p>
            </div>
            <span className={trained ? styles.ready : styles.draft}>
              {trained ? "Model ready" : "Not trained"}
            </span>
          </div>

          <label className={styles.uploadBox}>
            <input type="file" accept=".csv" onChange={handleFileChange} />
            <span className={styles.uploadIcon}>↑</span>
            <strong>Upload CSV file</strong>
            <small>Drag and drop or click to select your dataset</small>
            {fileName && (
              <div className={styles.fileName}>Selected: {fileName}</div>
            )}
          </label>

          {csvHeaders && (
            <div className={styles.csvPreview}>
              <strong>Preview</strong>
              <div className={styles.previewTableWrap}>
                <table className={styles.previewTable}>
                  <thead>
                    <tr>
                      {csvHeaders.map((h, i) => (
                        <th key={i}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {csvPreview.map((row, rIdx) => (
                      <tr key={rIdx}>
                        {row.map((c, cIdx) => (
                          <td key={cIdx}>{c}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className={styles.fieldGroup}>
            <div className={styles.fieldHeader}>
              <label>Training prompt</label>
              <span>{prompt.length}/500</span>
            </div>

            <textarea
              maxLength={500}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Example: Predict customer churn. Target column is churn. Use all useful numeric and categorical columns."
            />
          </div>

          <button
            className={styles.primaryButton}
            onClick={trainModel}
            disabled={training}
          >
            {training ? "Training model..." : "Train model"}
          </button>

          {(training || trained) && (
            <div className={styles.trainingBox}>
              <div className={styles.progressHeader}>
                <span>Training progress</span>
                <strong>{progress}%</strong>
              </div>

              <div className={styles.progressTrack}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {trained && (
            <button className={styles.downloadButton}>
              Download trained model
            </button>
          )}
        </div>

        <aside className={styles.sidePanel}>
          <h2>Try prediction</h2>
          <p>
            Test your trained model with one input row before downloading it.
          </p>
          <div className={styles.fieldGroup}>
            {/* <label className={styles.fieldLabel}>Choose Model</label> */}

            <select
              className={styles.select}
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              <option>--- Choose model ---</option>
              <option>Linear Regression</option>
              <option>Random Forest</option>
              <option>XGBoost</option>
              <option>LightGBM</option>
              <option>CatBoost</option>
              <option>Decision Tree</option>
              <option>Support Vector Machine</option>
              <option>KNN</option>
              <option>Neural Network (MLP)</option>
            </select>
          </div>

          <textarea
            value={prediction}
            onChange={(e) => setPrediction(e.target.value)}
            placeholder='Example: {"age": 24, "income": 52000, "city": "Berlin"}'
          />

          <button className={styles.secondaryButton} disabled={!trained}>
            Predict
          </button>

          <div className={styles.resultBox}>
            <span>Prediction output</span>
            <strong>
              {trained ? "Waiting for input..." : "Train a model first"}
            </strong>
          </div>
        </aside>
      </section>
    </main>
  );
}
