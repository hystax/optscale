// https://www.w3.org/MarkUp/html-spec/html-spec_13.html
export const HTML_SYMBOL = Object.freeze({
  colon: <>&#58;</>,
  comma: <>&#44;</>,
  period: <>&#46;</>
});

type HtmlSymbolProps = {
  symbol: keyof typeof HTML_SYMBOL;
};

const HtmlSymbol = ({ symbol }: HtmlSymbolProps) => HTML_SYMBOL[symbol];

export default HtmlSymbol;
