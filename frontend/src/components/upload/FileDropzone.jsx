import { useCallback, useRef, useState } from "react";
import styles from "./FileDropzone.module.css";

const ACCEPTED_TYPE = "application/pdf";

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * Drag-and-drop + click-to-browse PDF picker. Purely about collecting
 * files and showing what's selected — it has no idea how the upload
 * itself is progressing; that comes in via `uploadProgress` so this
 * component works the same whether an upload is in flight or not.
 */
export function FileDropzone({ files, onFilesChange, uploadProgress, disabled }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef(null);

  const addFiles = useCallback(
    (fileList) => {
      const pdfFiles = Array.from(fileList).filter((file) => file.type === ACCEPTED_TYPE);
      if (pdfFiles.length === 0) return;
      const existingNames = new Set(files.map((file) => file.name + file.size));
      const merged = [
        ...files,
        ...pdfFiles.filter((file) => !existingNames.has(file.name + file.size)),
      ];
      onFilesChange(merged);
    },
    [files, onFilesChange]
  );

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragActive(false);
    if (disabled) return;
    addFiles(event.dataTransfer.files);
  };

  const removeFile = (index) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div
        className={`${styles.dropzone} ${isDragActive ? styles.active : ""} ${
          disabled ? styles.disabled : ""
        }`}
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled) setIsDragActive(true);
        }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={handleDrop}
        onClick={() => !disabled && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if ((event.key === "Enter" || event.key === " ") && !disabled) {
            inputRef.current?.click();
          }
        }}
      >
        <p className={styles.instructions}>
          Drag and drop resume PDFs here, or click to browse
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          multiple
          disabled={disabled}
          className={styles.hiddenInput}
          onChange={(event) => {
            addFiles(event.target.files);
            event.target.value = "";
          }}
        />
      </div>

      {files.length > 0 && (
        <ul className={styles.fileList}>
          {files.map((file, index) => (
            <li key={file.name + file.size} className={styles.fileItem}>
              <span className={styles.fileName}>{file.name}</span>
              <span className={styles.fileSize}>{formatBytes(file.size)}</span>
              {!disabled && (
                <button
                  type="button"
                  className={styles.removeButton}
                  onClick={() => removeFile(index)}
                  aria-label={`Remove ${file.name}`}
                >
                  Remove
                </button>
              )}
            </li>
          ))}
        </ul>
      )}

      {uploadProgress != null && (
        <div className={styles.progressWrap}>
          <div
            className={styles.progressTrack}
            role="progressbar"
            aria-valuenow={uploadProgress}
            aria-valuemin={0}
            aria-valuemax={100}
          >
            <div className={styles.progressFill} style={{ width: `${uploadProgress}%` }} />
          </div>
          <span className={styles.progressLabel}>Uploading… {uploadProgress}%</span>
        </div>
      )}
    </div>
  );
}
