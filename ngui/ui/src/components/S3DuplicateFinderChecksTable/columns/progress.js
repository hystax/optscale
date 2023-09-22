import React from "react";
import CancelIcon from "@mui/icons-material/Cancel";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import { Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import CaptionedCell from "components/CaptionedCell";
import FormattedDuration from "components/FormattedDuration";
import HeaderHelperCell from "components/HeaderHelperCell";
import IconLabel from "components/IconLabel";
import KeyValueLabel from "components/KeyValueLabel";
import { STATUS } from "components/S3DuplicateFinderCheck/utils";
import SlicedText from "components/SlicedText";
import { getS3DuplicateFinderCheck } from "urls";
import { EN_FULL_FORMAT, format, millisecondsToSeconds, secondsToMilliseconds } from "utils/datetime";

const getCaption = ({ status, error, lastCompleted, lastRun }) => {
  if (status === STATUS.SUCCESS) {
    return (
      <KeyValueLabel
        variant="caption"
        messageId="duration"
        value={<FormattedDuration durationInSeconds={lastCompleted - lastRun} />}
      />
    );
  }
  if (status === STATUS.RUNNING) {
    return (
      <Typography variant="caption">
        <FormattedMessage
          id="inProgressFor"
          values={{ value: <FormattedDuration durationInSeconds={millisecondsToSeconds(new Date()) - lastRun} /> }}
        />
      </Typography>
    );
  }
  return <KeyValueLabel variant="caption" messageId="failed" value={<SlicedText limit={50} text={error} />} />;
};

const progress = () => ({
  header: (
    <HeaderHelperCell
      titleMessageId="progress"
      titleDataTestId="lbl_progress"
      helperMessageId="s3DuplicateFinderProgressHeaderDescription"
    />
  ),
  accessorKey: "created_at",
  defaultSort: "desc",
  cell: ({
    row: {
      original: { id, status, created_at: createdAt, last_error: error, last_completed: lastCompleted, last_run: lastRun }
    }
  }) => {
    const scheduleTime = format(secondsToMilliseconds(createdAt), EN_FULL_FORMAT);

    if ([STATUS.CREATED, STATUS.QUEUED].includes(status)) {
      return (
        <FormattedMessage
          id="scheduledAt"
          values={{
            label: scheduleTime
          }}
        />
      );
    }

    const caption = getCaption({ status, error, lastCompleted, lastRun });

    const { icon, label } = {
      [STATUS.SUCCESS]: {
        icon: <CheckCircleIcon fontSize="small" color="success" />,
        label: (
          <Link to={getS3DuplicateFinderCheck(id)} component={RouterLink}>
            {scheduleTime}
          </Link>
        )
      },
      [STATUS.RUNNING]: {
        icon: <PlayCircleIcon fontSize="small" color="primary" />,
        label: scheduleTime
      },
      [STATUS.FAILED]: {
        icon: <CancelIcon fontSize="small" color="error" />,
        label: scheduleTime
      }
    }[status];

    return (
      <CaptionedCell
        caption={[
          {
            node: caption,
            key: `progress-caption`
          }
        ]}
      >
        <IconLabel icon={icon} label={label} />
      </CaptionedCell>
    );
  }
});

export default progress;
