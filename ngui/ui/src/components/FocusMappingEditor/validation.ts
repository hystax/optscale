import { TEMPLATE_PLACEHOLDER_REGEX } from "./constants";

// Client-side checks that mirror the cheap rules of the backend mapping schema (validate_mapping); the server stays authoritative.
// The fields turn a failed check into a message themselves. Rule regexes are checked with isValidRegex (utils/validation).

export const hasColumnName = (columns: string[] | undefined) => (columns ?? []).some((column) => column.trim() !== "");

export const hasTemplatePlaceholder = (template: string | undefined) => TEMPLATE_PLACEHOLDER_REGEX.test(template ?? "");
