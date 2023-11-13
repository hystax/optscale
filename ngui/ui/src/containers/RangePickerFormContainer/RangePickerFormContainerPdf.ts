import PDFAble from "components/PDFAble/PDFAble";
import { intl } from "translations/react-intl-config";
import { formatUTC, FORMAT_YYYY_MM_DD } from "utils/datetime";
import { TYPES } from "utils/pdf";

class RangePickerFormContainerPdf extends PDFAble {
  pdfRender = () => {
    const { selectedStartDate, selectedEndDate } = this.data;

    const from = formatUTC(selectedStartDate);
    const to = formatUTC(selectedEndDate);
    const txtIntro = intl.formatMessage({ id: "dateRange" });
    const wholeMsg = `${txtIntro} ${intl.formatMessage({ id: "fromTo" }, { from, to })}`;

    const fromForFileName = formatUTC(selectedStartDate, FORMAT_YYYY_MM_DD);
    const toForFileName = formatUTC(selectedEndDate, FORMAT_YYYY_MM_DD);

    return [
      {
        type: TYPES.text,
        value: wholeMsg,
        fileNameData: { pdfId: this.props.pdfId, value: `${fromForFileName}_${toForFileName}` } // render for filename
      }
    ];
  };
}

export default RangePickerFormContainerPdf;
