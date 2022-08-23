import PDFAble from "components/PDFAble/PDFAble";
import { TYPES } from "utils/pdf";

class CanvasBarChartPdf extends PDFAble {
  pdfRender = () => [
    {
      type: TYPES.image,
      value: this.data.canvasRef.current
    }
  ];
}

export default CanvasBarChartPdf;
