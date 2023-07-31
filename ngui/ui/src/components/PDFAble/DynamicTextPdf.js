import PDFAble from "./PDFAble";

class DynamicTextPdf extends PDFAble {
  pdfRender = () => {
    const { text, elementType } = this.data;

    return [
      {
        type: elementType,
        value: text
      }
    ];
  };
}

export default DynamicTextPdf;
