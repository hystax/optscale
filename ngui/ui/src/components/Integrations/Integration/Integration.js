import React, { useEffect, useRef } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import { useTheme } from "@mui/material/styles";
import PropTypes from "prop-types";
import Backdrop from "components/Backdrop";
import TextBlock from "components/TextBlock";
import WrapperCard from "components/WrapperCard";
import { INTEGRATION_QUERY_PARAM } from "urls";
import { getQueryParams } from "utils/network";
import useStyles from "./Integration.styles";

const Integration = ({ title, button, blocks, withBackdrop = false, backdropMessage = {}, id }) => {
  const { [INTEGRATION_QUERY_PARAM]: active } = getQueryParams();
  const raised = id === active;
  const { classes } = useStyles();

  const cardRef = useRef(null);

  useEffect(() => {
    if (cardRef.current && raised) {
      cardRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [raised]);

  const theme = useTheme();

  return (
    <WrapperCard
      elevation={0}
      needAlign
      title={title}
      sx={{ backgroundColor: raised ? theme.palette.info.header : null }}
      raised={raised}
      ref={cardRef}
    >
      <Box height="100%" position="relative">
        {withBackdrop && (
          <Backdrop customClass="contentLoader">
            <Paper className={classes.paper} variant="elevation" elevation={3}>
              <TextBlock messageId={backdropMessage.id || "comingSoon"} values={backdropMessage.values} />
            </Paper>
          </Backdrop>
        )}
        <Box mb={2} className={classes.blocksWrapper}>
          {blocks.map((block) => block)}
        </Box>
        {button}
      </Box>
    </WrapperCard>
  );
};

Integration.propTypes = {
  title: PropTypes.node.isRequired,
  id: PropTypes.string.isRequired,
  blocks: PropTypes.arrayOf(PropTypes.node.isRequired).isRequired,
  button: PropTypes.node,
  withBackdrop: PropTypes.bool,
  backdropMessage: PropTypes.object
};

export default Integration;
