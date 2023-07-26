import React from "react";
import PropTypes from "prop-types";

// https://www.w3.org/MarkUp/html-spec/html-spec_13.html
export const HTML_SYMBOL = Object.freeze({
  colon: <>&#58;</>
});

const HtmlSymbol = ({ symbol }) => HTML_SYMBOL[symbol] ?? null;

HtmlSymbol.propTypes = {
  symbol: PropTypes.oneOf(["colon"])
};

export default HtmlSymbol;
