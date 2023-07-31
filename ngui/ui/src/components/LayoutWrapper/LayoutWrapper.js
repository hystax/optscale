import React, { Suspense } from "react";
import Container from "@mui/material/Container";
import PropTypes from "prop-types";
import ContentBackdropLoader from "components/ContentBackdropLoader";
import ErrorBoundary from "components/ErrorBoundary";
import useStyles from "./LayoutWrapper.styles";

const ComponentWrapper = ({ children }) => <Suspense fallback={<ContentBackdropLoader isLoading />}>{children}</Suspense>;

const LayoutWrapper = ({ component: Component, layout: Layout, context, mainMenu }) => {
  const { classes } = useStyles();

  return Layout ? (
    <Layout mainMenu={mainMenu}>
      <ComponentWrapper>
        <Component context={context} />
      </ComponentWrapper>
    </Layout>
  ) : (
    <Container component="main" className={classes.container}>
      <ErrorBoundary>
        <ComponentWrapper>
          <Component context={context} />
        </ComponentWrapper>
      </ErrorBoundary>
    </Container>
  );
};

ComponentWrapper.propTypes = {
  children: PropTypes.node.isRequired
};

LayoutWrapper.propTypes = {
  component: PropTypes.elementType.isRequired,
  layout: PropTypes.elementType,
  context: PropTypes.object,
  mainMenu: PropTypes.array
};

export default LayoutWrapper;
