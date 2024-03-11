import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SummaryList from "components/SummaryList";
import { isEmpty } from "utils/arrays";

const SUPPORTED_FILE_NAMES = ["expenses.csv", "recommendations.csv", "resources.csv"];

const isExportPathSupported = (path) => SUPPORTED_FILE_NAMES.some((name) => path.includes(name));

const getExportPathFileType = (exportFilePath) => {
  const fileName = SUPPORTED_FILE_NAMES.find((exportFileName) => exportFilePath.includes(exportFileName));

  return fileName?.split(".")[0];
};

const FilesSummaryList = ({ filePaths = [], isLoading }) => {
  const files = filePaths.filter(isExportPathSupported);

  return (
    <SummaryList
      titleMessage={<FormattedMessage id="files" />}
      isLoading={isLoading}
      items={
        isEmpty(files) ? (
          <FormattedMessage id="noFiles" />
        ) : (
          <>
            {files.map((filePath) => {
              const fileType = getExportPathFileType(filePath);

              return (
                <KeyValueLabel
                  key={fileType}
                  keyMessageId={fileType}
                  value={
                    <CopyText sx={{ fontWeight: "inherit" }} text={filePath}>
                      {filePath}
                    </CopyText>
                  }
                />
              );
            })}
          </>
        )
      }
    />
  );
};

export default FilesSummaryList;
