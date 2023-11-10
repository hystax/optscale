const ConditionWrapper = ({ condition, conditionTemplate = null, children = null }) => {
  const isSatisfied = typeof condition === "function" ? condition() : condition;
  return isSatisfied ? conditionTemplate : children;
};

export default ConditionWrapper;
