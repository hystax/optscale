import { useContext, useEffect, useState } from "react";
import CloseIcon from "@mui/icons-material/Close";
import { AppBar, Box, CircularProgress, Link, Paper, Toolbar } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { matchPath, useLocation } from "react-router-dom";
import IconButton from "components/IconButton";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import Markdown from "components/Markdown";
import SideModalTitle from "components/SideModalTitle";
import CommunityDocsContext from "contexts/CommunityDocsContext/CommunityDocsContext";
import { intl } from "translations/react-intl-config";
import { GITHUB_HYSTAX_OPTSCALE_REPO, getDocsFileUrl } from "urls";
import { SPACING_2 } from "utils/layouts";
import useStyles from "./DocsPanel.styles";

const STATUSES = {
  LOADING: "loading",
  OK: "ok",
  ERROR: "error",
  MISSING: "missing"
};

const GithubLink = (chunks) => (
  <Link href={GITHUB_HYSTAX_OPTSCALE_REPO} target="_blank" rel="noopener noreferrer">
    {chunks}
  </Link>
);

const DocumentationUrl = ({ url }: { url: string }) => <strong>ngui/ui/public{url}</strong>;

const DocsPanel = () => {
  const { classes } = useStyles();
  const { isCommunityDocsOpened, setIsCommunityDocsOpened, allRoutesPatterns } = useContext(CommunityDocsContext);

  const [status, setStatus] = useState(STATUSES.LOADING);

  const [markdown, setMarkdown] = useState("");

  const { pathname } = useLocation();
  const [currentMatch] = allRoutesPatterns.filter((pattern) => matchPath(pattern, pathname));

  const documentationUrl = getDocsFileUrl(currentMatch);

  useEffect(() => {
    if (!isCommunityDocsOpened) {
      return undefined;
    }

    const controller = new AbortController();
    const { signal } = controller;

    async function loadHelp() {
      try {
        setStatus(STATUSES.LOADING);
        const response = await fetch(documentationUrl, { signal });
        if (response.headers.get("content-type")?.startsWith("text/markdown")) {
          const text = await response.text();
          setMarkdown(text);
          setStatus(STATUSES.OK);
        } else {
          setStatus(STATUSES.MISSING);
        }
      } catch ({ name }) {
        // if not just updated useEffect and aborted loading
        if (name !== "AbortError") {
          setStatus(STATUSES.ERROR);
        }
      }
    }

    loadHelp();

    return () => controller.abort();
  }, [documentationUrl, isCommunityDocsOpened]);

  return (
    <Paper className={classes.wrapper} elevation={0}>
      <AppBar color="info" position="static">
        <Toolbar className={classes.toolbar}>
          <SideModalTitle sx={{ flexGrow: 1 }}>
            <FormattedMessage id="communityDocs" />
          </SideModalTitle>
          <IconButton icon={<CloseIcon />} onClick={setIsCommunityDocsOpened} color="inherit" />
        </Toolbar>
      </AppBar>
      <Box className={classes.content}>
        {status === STATUSES.LOADING && (
          <Box className={classes.loader}>
            <CircularProgress />
          </Box>
        )}
        {status === STATUSES.OK && (
          <>
            <Box m={SPACING_2}>
              <Markdown>{markdown}</Markdown>
            </Box>
            <InlineSeverityAlert
              messageId="contributeToDocs"
              messageValues={{
                documentationUrl: <DocumentationUrl url={documentationUrl} />,
                github: GithubLink,
                action: intl.formatMessage({ id: "edit" }).toLocaleLowerCase()
              }}
            />
          </>
        )}
        {status === STATUSES.MISSING && (
          <InlineSeverityAlert
            messageId="noCommunityDocumentation"
            messageValues={{
              br: <br />,
              contributeMessage: (
                <FormattedMessage
                  id="contributeToDocs"
                  values={{
                    documentationUrl: <DocumentationUrl url={documentationUrl} />,
                    github: GithubLink,
                    action: intl.formatMessage({ id: "add" }).toLocaleLowerCase()
                  }}
                />
              )
            }}
          />
        )}
        {status === STATUSES.ERROR && <FormattedMessage id="communityDocsError" />}
      </Box>
    </Paper>
  );
};

export default DocsPanel;
