export const handleChange = (state, changeState) => (updater) => {
  changeState(updater(state));
};
