export const useShouldRenderLoader = (isInitialMount, loadingStates) => {
  // We need the isInitialMount to prevent rendering of the child component on the first mount
  const isLoading = loadingStates.some((loadingState) => loadingState);
  return isInitialMount || isLoading;
};
