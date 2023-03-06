/**
 * Based on the library logic:
 * ```
 *   let id =
 *    resolvedColumnDef.id ??
 *    (accessorKey ? accessorKey.replace('.', '_') : undefined) ??
 *    (typeof resolvedColumnDef.header === 'string'
 *      ? resolvedColumnDef.header
 *      : undefined)
 * ```
 */
export const getColumnId = (columnDefinition) => {
  const { id, accessorKey, header } = columnDefinition;

  return id ?? (accessorKey ? accessorKey.replace(".", "_") : undefined) ?? (typeof header === "string" ? header : undefined);
};
