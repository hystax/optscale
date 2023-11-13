// https://www.w3.org/MarkUp/html-spec/html-spec_13.html
export const HTML_SYMBOL = Object.freeze({
  colon: <>&#58;</>
});

const HtmlSymbol = ({ symbol }) => HTML_SYMBOL[symbol] ?? null;

export default HtmlSymbol;
