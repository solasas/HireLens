import { forwardRef } from "react";
import styles from "./Button.module.css";

/** variant: "primary" | "secondary" */
export const Button = forwardRef(function Button(
  { variant = "primary", disabled, children, ...rest },
  ref
) {
  return (
    <button
      ref={ref}
      className={`${styles.button} ${styles[variant]}`}
      disabled={disabled}
      {...rest}
    >
      {children}
    </button>
  );
});
