// Accepted entries are MIME types or extensions (".csv"), like the accept attribute of a file input.
// The MIME type of a file depends on the browser and the OS, so a file with an accepted extension is accepted
// whatever type it is reported with.
export const isAcceptedFile = (file: Pick<File, "name" | "type">, acceptedFiles: string[]) =>
  acceptedFiles.includes(file.type) ||
  acceptedFiles.some(
    (acceptedFile) => acceptedFile.startsWith(".") && file.name.toLowerCase().endsWith(acceptedFile.toLowerCase())
  );
