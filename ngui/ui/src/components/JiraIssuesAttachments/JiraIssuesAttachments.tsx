import { useState } from "react";
import Link from "@mui/material/Link";
import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { splitIntoTwoChunks, isEmpty as isEmptyArray } from "utils/arrays";
import useStyles from "./JiraIssuesAttachments.styles";

const JiraIssueListItem = ({ issueName, link }) => (
  <li>
    <Link href={link} target="_blank" rel="noopener noreferrer">
      {issueName}
    </Link>
  </li>
);

const ToggleListItem = ({ onClick, label }) => {
  const { classes } = useStyles();

  return <li className={classes.toggleListItem}>{<DashedTypography onClick={onClick}>{label}</DashedTypography>}</li>;
};

const JiraIssuesListItems = ({ issues }) =>
  issues.map(({ issue_link: issueLink, project_key: projectKey, issue_number: issueNumber }) => (
    <JiraIssueListItem key={issueNumber} link={issueLink} issueName={`${projectKey}-${issueNumber}`} />
  ));

const LIMIT = 5;

const JiraIssuesAttachments = ({ issues }) => {
  const { classes } = useStyles();

  const [isExpanded, setIsExpanded] = useState(false);

  const [firstIssuesChunk, secondIssuesChunk] = splitIntoTwoChunks(issues, LIMIT);

  const renderExpander = () =>
    isExpanded ? (
      <>
        <JiraIssuesListItems issues={secondIssuesChunk} />
        <ToggleListItem label={<FormattedMessage id="showLess" />} onClick={() => setIsExpanded(false)} />
      </>
    ) : (
      <ToggleListItem label={<FormattedMessage id="showMore" />} onClick={() => setIsExpanded(true)} />
    );

  return (
    <div>
      <KeyValueLabel keyMessageId="jiraIssues" value={issues.length} />
      {!isEmptyArray(firstIssuesChunk) && (
        <ul className={classes.list}>
          <JiraIssuesListItems issues={firstIssuesChunk} />
          {!isEmptyArray(secondIssuesChunk) && renderExpander()}
        </ul>
      )}
    </div>
  );
};

export default JiraIssuesAttachments;
