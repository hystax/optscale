import { FormattedMessage } from "react-intl";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import SummaryList from "components/SummaryList";
import { isEmpty } from "utils/arrays";

type FilesSummaryListProps = {
  filePaths?: string[];
  isLoading?: boolean;
};

const getFiles = (files: string[]) =>
  files.map((file) => {
    switch (true) {
      case file.includes("expenses.csv"):
        return {
          path: file,
          type: "expenses"
        } as const;
      case file.includes("recommendations.csv"):
        return {
          path: file,
          type: "recommendations"
        } as const;
      case file.includes("resources.csv"):
        return {
          path: file,
          type: "resources"
        } as const;
      default:
        return {
          path: null,
          type: ""
        } as const;
    }
  });

const FilesSummaryList = ({ filePaths = [], isLoading }: FilesSummaryListProps) => {
  const files = getFiles(filePaths);

  return (
    <SummaryList
      titleMessage={<FormattedMessage id="files" />}
      isLoading={isLoading}
      items={
        isEmpty(files) ? (
          <FormattedMessage id="noFiles" />
        ) : (
          <>
            {files.map(
              ({ path, type }) =>
                path && (
                  <KeyValueLabel
                    key={type}
                    keyMessageId={type}
                    value={
                      <CopyText sx={{ fontWeight: "inherit" }} text={path}>
                        {path}
                      </CopyText>
                    }
                  />
                )
            )}
          </>
        )
      }
    />
  );
};

export default FilesSummaryList;
