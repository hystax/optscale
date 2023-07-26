import { jsPDF as JSPDF } from "jspdf";
import { PDF_THEME } from "theme";
import { intl } from "translations/react-intl-config";
import { PRODUCTION as URL_PRODUCTION } from "urls";
import { PDF_ELEMENTS } from "utils/constants";
import UbuntuFilePath from "../assets/fonts/Ubuntu-Regular.ttf";
import "jspdf-autotable";
import logo from "../assets/logo/logo_pdf.png";

const defaultFileName = "optscale-report-%___time___%";
let fileName = "";
let alsoRenderIntoFileName = {}; // pairs of (pdfId, "%patternName%"")

// types for reactive-content pdf elements — elements with PDFAble child
const TYPES = {
  text: "text",
  simpleSummaryCard: "simple summary card",
  image: "image"
};

// renders "heap" — just object with id-render props
const renders = {};

const addToPdfElementsHeap = (pdfRender, pdfId) => {
  renders[pdfId] = pdfRender;
};

const removeFromPdfElementsHeap = (pdfId) => {
  renders[pdfId] = undefined;
};

const portraitSettings = {
  initialY: 40,
  pageMarginLR: 20,
  summaryGridColumns: 3,
  spacingV: 5,
  spacingH: 5
};

const landscapeSettings = {
  initialY: 40,
  pageMarginLR: 20,
  summaryGridColumns: 4,
  spacingV: 10,
  spacingH: 5
};

let currentSettings = portraitSettings;

let cursorY = currentSettings.initialY;
let currentColumn = 0;
let nextElementIsSameType = false;
let prevElementIsSameType = false;

const checkAvailablePageSpace = ({ doc, dy, addPage = true, moveCursor = true }) => {
  const pageHeight = doc.internal.pageSize.height;
  let result = false;

  if (cursorY + dy > pageHeight - currentSettings.initialY) {
    if (addPage) {
      doc.addPage();
      cursorY = currentSettings.initialY;
    }
    result = false;
  } else {
    if (moveCursor) {
      cursorY += dy;
    }
    result = true;
  }
  return result;
};

const addSpacing = () => {
  cursorY += currentSettings.spacingV;
};

// https://gist.github.com/AnalyzePlatypus/c54d520e9bd5b5f662aeb0276e3f01a4
// Assumes your document using is `pt` units
// If you're using any other unit (mm, px, etc.) use this gist to translate: https://gist.github.com/AnalyzePlatypus/55d806caa739ba6c2b27ede752fa3c9c
const addWrappedText = (doc, text, fontSize) => {
  doc.setFontSize(fontSize);
  const textWidth = doc.internal.pageSize.width - currentSettings.pageMarginLR * 2;
  const textLines = doc.splitTextToSize(text, textWidth); // Split the text into lines

  textLines.forEach((lineText) => {
    checkAvailablePageSpace({ doc, dy: fontSize, addPage: true, moveCursor: true });
    doc.text(currentSettings.pageMarginLR, cursorY, lineText);
    addSpacing();
  });
};

const createNothing = () => undefined;

const createFooter = (doc) => {
  const text = intl.formatMessage({ id: "pdfFooterNote" });
  const link = intl.formatMessage({ id: "pdfFooterNoteLink" });

  doc.setFontSize(PDF_THEME.fontSizes.footerNote);
  const y = doc.internal.pageSize.height - currentSettings.initialY / 2;
  const x = currentSettings.pageMarginLR;
  const textWidth = doc.getTextWidth(text);
  const savedColor = doc.getTextColor();
  doc.text(x, y, text);
  doc.setTextColor(PDF_THEME.colors.link);
  doc.textWithLink(link, x + textWidth, y, { url: URL_PRODUCTION });
  doc.setTextColor(savedColor);
};

// todo: I bet it wont work right after more pages added (image will appear on the last page)
const createLogo = (doc) => {
  const imageWidth = 100;
  const imageX = doc.internal.pageSize.width - currentSettings.pageMarginLR - imageWidth;
  doc.addImage(logo, "PNG", imageX, 20, imageWidth, 30);
};

const createH1 = (doc, value, parameters) => {
  addWrappedText(doc, intl.formatMessage({ id: value }, parameters.data), PDF_THEME.fontSizes.h1);
};

const createH2 = (doc, value, parameters) => {
  addWrappedText(doc, intl.formatMessage({ id: value }, parameters.data), PDF_THEME.fontSizes.h2);
};

const createText = (doc, value, parameters) => {
  addWrappedText(doc, value, parameters.fontSize ?? PDF_THEME.fontSizes.text);
};

const createNewPortraitPage = (doc) => {
  doc.addPage("a4", "p");
  currentSettings = portraitSettings;
  cursorY = currentSettings.initialY;
};

const createNewLandscapePage = (doc) => {
  doc.addPage("a4", "l");
  currentSettings = landscapeSettings;
  cursorY = currentSettings.initialY;
};

const createSummaryCard = (doc, value, parameters) => {
  const spacer = currentSettings.spacingH;
  const pageMargin = currentSettings.pageMarginLR;
  const columns = currentSettings.summaryGridColumns;
  const columnSize = (doc.internal.pageSize.width - pageMargin * 2 - spacer * (columns - 1)) / columns;

  const margin = {};
  margin.left = pageMargin + columnSize * currentColumn + spacer * currentColumn;

  const smallFont = PDF_THEME.fontSizes.summarySmall;
  const bigFont = PDF_THEME.fontSizes.summaryBig;
  const paddingSmall = { top: 5, bottom: 3, left: 5, right: 5 };
  const paddingBig = { top: 0, bottom: 5, left: 5, right: 0 };
  const heightTotal =
    smallFont * 1.15 + bigFont * 1.15 + paddingSmall.top + paddingSmall.bottom + paddingBig.top + paddingBig.bottom; // todo: will work only for cards without wordwrap
  checkAvailablePageSpace({ doc, dy: heightTotal, addPage: true, moveCursor: false });

  doc.autoTable({
    head: [["", ""]],
    body: [
      ["", parameters.header],
      ["", value]
    ],
    showHead: false,
    startY: cursorY,
    theme: "plain",
    margin,
    tableWidth: columnSize,

    // Use for changing styles with jspdf functions or customize the positioning of cells or cell text
    // just before they are drawn to the page.
    didParseCell: (data) => {
      const cellStyle = data.cell.styles;
      const rowIndex = data.row.index;

      cellStyle.cellPadding = paddingSmall;
      cellStyle.fontSize = smallFont;

      if (rowIndex === 1) {
        cellStyle.fontSize = bigFont;
        cellStyle.cellPadding = paddingBig;
      }
    },

    tableLineColor: parameters.color,
    tableLineWidth: 1,
    styles: {
      lineWidth: 0,
      overflow: "linebreak",
      font: "Ubuntu"
    },

    columnStyles: {
      0: {
        fillColor: parameters.color,
        textColor: 255,
        cellWidth: 5,
        valign: "bottom"
      },
      1: {
        valign: "middle"
      }
    }
  });

  currentColumn += 1;
  if (currentColumn >= currentSettings.summaryGridColumns || !nextElementIsSameType) {
    cursorY = doc.lastAutoTable.finalY + currentSettings.spacingV; // todo: won't work for cards with different heights (big first)
    currentColumn = 0;
  }
};

// "rendering" static filename fields
const createFileName = (doc, value, parameters) => {
  alsoRenderIntoFileName = {};
  // searching for %% in string
  const renderedFileName = value.replace(/%(.*?)%/g, (strPattern, link) => {
    if (link === "___time___") {
      // def filename option
      const date = new Date();
      return `${date.getHours()}_${date.getMinutes()}_${date.getSeconds()}`;
    }

    if (parameters[link]) {
      const { data, type = "string" } = parameters[link];

      if (type === "string") {
        return data;
      }

      if (type === "object") {
        alsoRenderIntoFileName[data] = strPattern; // other pdf objects will check, if they need to update filename with their content
        return strPattern;
      }
    }

    return "";
  });

  fileName = `${renderedFileName}.pdf`;
};

const createImage = async (doc, value) => {
  const scaleCoeff = Math.min(doc.internal.pageSize.width / value.width, 1); // scale to: a4 width, or no scale if width is smaller than a4 width
  const finalHeight = value.height * scaleCoeff;

  checkAvailablePageSpace({ doc, dy: finalHeight, addPage: true, moveCursor: false });
  doc.addImage(value, "PNG", 0, cursorY, value.width * scaleCoeff, finalHeight, undefined, "FAST");
  cursorY += finalHeight;
};

const updateFileName = (fileNameData) => {
  if (!fileNameData) return;

  const fileNamePattern = alsoRenderIntoFileName[fileNameData.pdfId];
  if (fileNamePattern) {
    // file name depends from object with that pdfId
    fileName = fileName.replace(fileNamePattern, fileNameData.value);
  }
};

const TYPES_RENDERS = {
  [TYPES.text]: createText,
  [TYPES.simpleSummaryCard]: createSummaryCard,
  [TYPES.image]: createImage,
  [PDF_ELEMENTS.markup.newPortraitPage]: createNewPortraitPage,
  [PDF_ELEMENTS.markup.newLandscapePage]: createNewLandscapePage,
  [PDF_ELEMENTS.markup.logo]: createLogo,
  [PDF_ELEMENTS.markup.initLandscape]: createNothing,
  [PDF_ELEMENTS.markup.initPortrait]: createNothing,
  [PDF_ELEMENTS.markup.spacer]: addSpacing,
  [PDF_ELEMENTS.markup.footer]: createFooter,
  [PDF_ELEMENTS.basics.H1]: createH1,
  [PDF_ELEMENTS.basics.H2]: createH2,
  [PDF_ELEMENTS.basics.fileName]: createFileName
};

const loadFont = (doc, { font, vfsName, name, style }) =>
  new Promise((accept, reject) => {
    fetch(font)
      .then((response) => response.blob())
      .then((blob) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          if (e.target.result) {
            const fontBase64String = e.target.result.substr(e.target.result.indexOf(",") + 1); // without meta
            doc.addFileToVFS(vfsName, fontBase64String);
            doc.addFont(vfsName, name, style);
            doc.setFont(name);
            accept();
          } else {
            reject();
          }
        };
        reader.readAsDataURL(blob);
      })
      .catch(reject);
  });

const createPdf = async (elements) => {
  createFileName(null, defaultFileName);

  // gathering elements data from renders
  let docElements = [];
  elements.forEach((el) => {
    if (Object.prototype.hasOwnProperty.call(el, "type")) {
      docElements.push(el);
    } else if (Object.prototype.hasOwnProperty.call(el, "id")) {
      if (renders[el.id]) docElements = docElements.concat(renders[el.id]());
    }
  });

  // initial doc settings
  const initialSettings = { orientation: "p", units: "pt", size: "a4" };
  if (docElements[0].type === PDF_ELEMENTS.markup.initLandscape) {
    initialSettings.orientation = "l";
    currentSettings = landscapeSettings;
  } else if (docElements[0].type === PDF_ELEMENTS.markup.initPortrait) {
    currentSettings = portraitSettings;
  } else {
    console.warn("utils/pdf.js: please, add markup.initLandscape or initPortrait pdf element as first one!");
  }

  cursorY = currentSettings.initialY;

  const doc = new JSPDF(initialSettings.orientation, initialSettings.units, initialSettings.size);
  await loadFont(doc, {
    font: UbuntuFilePath,
    vfsName: "Ubuntu-Regular.ttf",
    name: "Ubuntu",
    style: "normal"
  });

  // elements to doc one by one
  const awaitResults = [];
  for (let i = 0; i < docElements.length; i += 1) {
    const { type, value = "", parameters = {}, fileNameData } = docElements[i];

    nextElementIsSameType = i + 1 < docElements.length && docElements[i + 1].type === type;
    prevElementIsSameType = i > 0 && docElements[i - 1].type === type;
    if (!prevElementIsSameType) currentColumn = 0;

    const typeRender = TYPES_RENDERS[type];
    const result = typeRender(doc, value, parameters);

    if (result) awaitResults.push(result);

    updateFileName(fileNameData);
  }

  await Promise.all(awaitResults);

  // saving document
  doc.save(fileName);
};

export { createPdf, addToPdfElementsHeap, removeFromPdfElementsHeap, TYPES };
