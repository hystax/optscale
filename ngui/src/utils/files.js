const ZIP = "zip";
const GZIP = "gz";
const CSV = "csv";

const cloudReportExtensions = Object.freeze([GZIP, ZIP, CSV]);
const codeReportExtensions = Object.freeze([ZIP]);

const getFileExtension = (fileName) => fileName.split(".").pop();

const isExtensionSupported = (fileName, supportedExtensions) => supportedExtensions.includes(getFileExtension(fileName));

export const isCloudReportExtensionSupported = (moduleName) => isExtensionSupported(moduleName, cloudReportExtensions);

export const isCodeReportExtensionSupported = (moduleName) => isExtensionSupported(moduleName, codeReportExtensions);
