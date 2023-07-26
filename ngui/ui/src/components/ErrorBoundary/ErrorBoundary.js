import React from "react";
import PropTypes from "prop-types";
import SomethingWentWrong from "components/SomethingWentWrong";

class ErrorBoundary extends React.Component {
  static defaultProps = {
    FallbackComponent: SomethingWentWrong
  };

  state = {
    error: null,
    info: null
  };

  componentDidCatch(error, info) {
    this.setState({ error, info });
  }

  render() {
    const { FallbackComponent } = this.props;
    return this.state.error === null ? this.props.children : <FallbackComponent />;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  FallbackComponent: PropTypes.elementType
};

export default ErrorBoundary;
