import PDFAble from "components/PDFAble/PDFAble";
import { PDF_ELEMENTS } from "utils/constants";

class WrapperCardTitlePdf extends PDFAble {
  pdfRender = () => {
    const { titleText } = this.data;

    return [
      {
        type: PDF_ELEMENTS.basics.H2,
        value: titleText
      }
    ];
  };
}

export default WrapperCardTitlePdf;
