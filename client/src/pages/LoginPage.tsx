import styles from "./Page.module.css";
import { Link } from "react-router-dom";

export default function LoginPage() {
  return (
    <main className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Login</h1>
        <p className={styles.text}>Sign in to your account.</p>

        <input
          className={styles.input}
          type="email"
          placeholder="Email"
        />

        <input
          className={styles.input}
          type="password"
          placeholder="Password"
        />

        <button className={styles.button}>Login</button>

        <div className={styles.link}>
          <Link to="/create-account">Create an account</Link>
        </div>
      </div>
    </main>
  );
}