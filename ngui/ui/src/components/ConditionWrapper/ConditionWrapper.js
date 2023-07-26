import PropTypes from "prop-types";

const ConditionWrapper = ({ condition, conditionTemplate = null, children = null }) => {
  const isSatisfied = typeof condition === "function" ? condition() : condition;
  return isSatisfied ? conditionTemplate : children;
};

ConditionWrapper.propTypes = {
  condition: PropTypes.oneOfType([PropTypes.func, PropTypes.bool]).isRequired,
  conditionTemplate: PropTypes.node,
  children: PropTypes.node
};

export default ConditionWrapper;
