import { Component } from "react";
import SomethingWentWrong from "components/SomethingWentWrong";

class ErrorBoundary extends Component {
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

export default ErrorBoundary;
