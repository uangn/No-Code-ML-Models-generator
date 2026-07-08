import { useNavigate } from "react-router-dom";
import styles from "./HomePage.module.css";

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <main className={styles.page}>
      <nav className={styles.navbar}>
        <div className={styles.logo}>NoCodeML</div>
        <div>
        <button
          className={styles.navButton}
          onClick={() => navigate("/login")}
        >
          Login
        </button>

        <button
          className={styles.secondaryButton}
          onClick={() => navigate("/create-account")}
        >
          Create account
        </button>
        </div>
      </nav>

      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <span className={styles.badge}>No-code machine learning</span>

          <h1 className={styles.title}>
            Build ML models without writing code
          </h1>

          <p className={styles.subtitle}>
            No Code ML Models Generator helps you upload data, choose a goal,
            train models, and generate predictions through a simple visual
            workflow.
          </p>

          <div className={styles.actions}>
            <button
              className={styles.primaryButton}
              onClick={() => navigate("/product")}
            >
              Get started
            </button>

          </div>
        </div>

        <div className={styles.previewCard}>
          <div className={styles.windowBar}>
            <span />
            <span />
            <span />
          </div>

          <div className={styles.previewContent}>
            <p className={styles.previewLabel}>Model Builder</p>
            <h2>Sales Prediction</h2>

            <div className={styles.pipeline}>
              <div>Upload CSV</div>
              <div>Select Target</div>
              <div>Train Model</div>
              <div>Download Result</div>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.features}>
        <div className={styles.featureCard}>
          <h3>Upload datasets</h3>
          <p>Import CSV files and prepare your data in minutes.</p>
        </div>

        <div className={styles.featureCard}>
          <h3>Auto-train models</h3>
          <p>Generate classification or regression models automatically.</p>
        </div>

        <div className={styles.featureCard}>
          <h3>No coding needed</h3>
          <p>Describe your goal and let the system build the ML pipeline.</p>
        </div>
      </section>
    </main>
  );
}