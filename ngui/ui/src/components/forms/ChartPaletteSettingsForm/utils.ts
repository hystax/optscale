export const getDefaultValues = (palette, options) => ({
  [palette]: options.map((option) => ({ color: option }))
});
