import { useState, useRef } from "react";

const useDropzone = ({ onChange }) => {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [highlight, setHighlight] = useState(false);

  // Add support for multiple files upload
  const onFilesAdded = ([addedFile]) => {
    setFile(addedFile);
    onChange(addedFile);
  };

  const onFilesRemoved = (event) => {
    // Do not trigger an open file dialog window
    event.stopPropagation();
    // Clear the reference to be able to reselect the same file right after removing it
    fileInputRef.current.value = null;
    setFile(null);
    onChange(null);
  };

  const openFileDialog = () => {
    fileInputRef.current.click();
  };

  const onDragOver = (event) => {
    event.preventDefault();
    setHighlight(true);
  };

  const onDragLeave = () => setHighlight(false);

  const onDrop = (event) => {
    event.preventDefault();
    setHighlight(false);

    const { files } = event.dataTransfer;
    onFilesAdded(files);
  };

  return {
    fileInputRef,
    file,
    highlight,
    onFilesAdded,
    onFilesRemoved,
    openFileDialog,
    onDragOver,
    onDragLeave,
    onDrop
  };
};

export default useDropzone;
