import PDFAble from "components/PDFAble/PDFAble";
import { TYPES } from "utils/pdf";

class BarChartPdf extends PDFAble {
  pdfRender = () => [
    {
      type: TYPES.svg,
      value: this.props.pdfId
    }
  ];
}

export default BarChartPdf;
