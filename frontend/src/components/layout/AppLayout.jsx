import { Outlet } from "react-router-dom";
import { NavBar } from "./NavBar";
import styles from "./AppLayout.module.css";

export function AppLayout() {
  return (
    <div className={styles.shell}>
      <NavBar />
      <main className={styles.content}>
        <Outlet />
      </main>
    </div>
  );
}
