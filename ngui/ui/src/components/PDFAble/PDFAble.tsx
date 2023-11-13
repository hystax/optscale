import { Component } from "react";
import { addToPdfElementsHeap, removeFromPdfElementsHeap } from "utils/pdf";

class PDFAble extends Component {
  /* eslint-disable-next-line class-methods-use-this --
   *   TODO: To discuss if we need this method. The pdf generation doesn't work if the child class doesn't override this method.
   *   Perhaps we should either remove it, or add a fallback value, for example, we could try render the component name, or some "empty" text ("Something went wrong")
   */
  pdfRender = () => {};

  // updating values before adding to pdf
  pdfRenderBase = () => {
    if (typeof this.props.renderData === "function") {
      this.data = this.props.renderData();
    }
    return this.pdfRender();
  };

  componentDidMount = () => {
    addToPdfElementsHeap(this.pdfRenderBase, this.props.pdfId);
  };

  componentWillUnmount = () => {
    removeFromPdfElementsHeap(this.props.pdfId);
  };

  /* eslint-disable-next-line class-methods-use-this --
   * The instance must have the "render", method
   */
  render = () => null;
}

export default PDFAble;
