export type PickRename<T, R extends { [K in keyof R]: K extends keyof T ? PropertyKey : "Error: key not in T" }> = {
  [P in keyof T as P extends keyof R ? R[P] : P]: T[P];
};

export type ObjectKeys<T extends Record<string, unknown>> = keyof T;

export type ObjectValues<T extends Record<string, unknown>> = T[ObjectKeys<T>];

export type ArrayValues<T extends readonly unknown[]> = T[number];
