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
  })[type];

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

export default Brackets;
