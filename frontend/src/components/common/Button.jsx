import { forwardRef } from "react";
import styles from "./Button.module.css";

/** variant: "primary" | "secondary" | "danger"; size: "md" | "sm" */
export const Button = forwardRef(function Button(
  { variant = "primary", size = "md", disabled, children, ...rest },
  ref
) {
  return (
    <button
      ref={ref}
      className={`${styles.button} ${styles[variant]} ${size === "sm" ? styles.sm : ""}`}
      disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  );
});
