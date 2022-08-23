import React from "react";
import PropTypes from "prop-types";

const getBrackets = (type) =>
  ({
    round: {
      opening: "(",
      closing: ")"
    },
    curly: {
      opening: "{",
      closing: "}"
    },
    square: {
      opening: "[",
      closing: "]"
    },
    angle: {
      opening: "<",
      closing: ">"
    }
  }[type]);

const Brackets = ({ children, type = "round", bold = false }) => {
  const { opening: openingBracket, closing: closingBracket } = getBrackets(type);
  return (
    <>
      {bold ? <strong>{openingBracket}</strong> : openingBracket}
      {children || " "}
      {bold ? <strong>{closingBracket}</strong> : closingBracket}
    </>
  );
};

Brackets.propTypes = {
  children: PropTypes.node,
  type: PropTypes.oneOf(["round", "curly", "square", "angle"]),
  bold: PropTypes.bool
};

export default Brackets;
