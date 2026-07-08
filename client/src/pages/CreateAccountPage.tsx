import { Link } from "react-router-dom";
import styles from "./Page.module.css";

export default function CreateAccountPage() {
  return (
    <main className={styles.page}>
      <div className={styles.card}>
        <h1 className={styles.title}>Create Account</h1>
        <p className={styles.text}>
          Create your account to get started.
        </p>

        <input
          className={styles.input}
          type="text"
          placeholder="Username"
        />

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

        <input
          className={styles.input}
          type="password"
          placeholder="Confirm Password"
        />

        <button className={styles.button}>
          Create Account
        </button>

        <div className={styles.link}>
          Already have an account?{" "}
          <Link to="/login">Sign in</Link>
        </div>
      </div>
    </main>
  );
}