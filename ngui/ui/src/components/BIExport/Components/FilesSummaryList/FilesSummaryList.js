import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel";
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
                  messageId={fileType}
                  value={
                    <CopyText text={filePath}>
                      <strong>{filePath}</strong>
                    </CopyText>
                  }
                  typographyProps={{
                    valueStyle: {
                      whiteSpace: "normal",
                      overflowWrap: "anywhere"
                    }
                  }}
                />
              );
            })}
          </>
        )
      }
    />
  );
};

FilesSummaryList.propTypes = {
  filePaths: PropTypes.array,
  isLoading: PropTypes.bool
};

export default FilesSummaryList;
