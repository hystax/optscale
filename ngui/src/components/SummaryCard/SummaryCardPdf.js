import PDFAble from "components/PDFAble/PDFAble";
import { intl } from "translations/react-intl-config";
import { TYPES } from "utils/pdf";

class SummaryCardPdf extends PDFAble {
  pdfRender = () => [
    {
      type: TYPES.simpleSummaryCard,
      value: intl.formatNumber(this.data.rawValue, { format: this.data.currency || "USD" }).toLocaleLowerCase(),
      parameters: {
        header: intl.formatMessage({ id: this.data.rawCaption }),
        color: this.data.color
      }
    }
  ];
}

export default SummaryCardPdf;
