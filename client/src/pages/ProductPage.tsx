import { useState } from "react";
import styles from "./ProductPage.module.css";

export default function ProductPage() {
  const [prompt, setPrompt] = useState("");
  const [training, setTraining] = useState(false);
  const [progress, setProgress] = useState(0);
  const [trained, setTrained] = useState(false);
  const [prediction, setPrediction] = useState("");
  const [model, setModel] = useState("Auto");

  const trainModel = () => {
    setTraining(true);
    setTrained(false);
    setProgress(0);

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
            <input type="file" accept=".csv" />
            <span className={styles.uploadIcon}>↑</span>
            <strong>Upload CSV file</strong>
            <small>Drag and drop or click to select your dataset</small>
          </label>

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
              <option>
                  --- Choose model ---
                </option>
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

          <button
            className={styles.secondaryButton}
            disabled={!trained}
          >
            Predict
          </button>

          <div className={styles.resultBox}>
            <span>Prediction output</span>
            <strong>{trained ? "Waiting for input..." : "Train a model first"}</strong>
          </div>
        </aside>
      </section>
    </main>
  );
}