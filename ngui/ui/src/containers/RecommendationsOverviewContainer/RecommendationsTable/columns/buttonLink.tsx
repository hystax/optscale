import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Box, Link, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import QuestionMark from "components/QuestionMark";
import TextWithDataTestId from "components/TextWithDataTestId";

const buttonLink = ({ headerDataTestId, accessorKey, onClick }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="name" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: (cellData) => {
    const {
      cell,
      row: {
        original: { recommendation }
      }
    } = cellData;

    return (
      <CaptionedCell
        caption={{
          key: "error",
          node: recommendation.hasError && (
            <Box display="flex" alignItems="center">
              <Typography color="error" variant="caption">
                <FormattedMessage id="recommendationError" />
              </Typography>
              <QuestionMark fontSize="small" tooltipText={recommendation.error} color="error" Icon={ErrorOutlineOutlinedIcon} />
            </Box>
          )
        }}
      >
        <Link
          component="button"
          style={{
            textAlign: "left"
          }}
          variant="body2"
          onClick={() => onClick(cellData)}
        >
          <FormattedMessage id={cell.getValue()} />
        </Link>
      </CaptionedCell>
    );
  }
});

export default buttonLink;
