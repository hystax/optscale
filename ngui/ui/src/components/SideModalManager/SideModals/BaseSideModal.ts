class BaseSideModal {
  constructor(userPayload = {}, close = () => {}) {
    this.initialize(userPayload);
    this.closeSideModal = close;
  }

  initialize(userPayload) {
    this.payload = userPayload;
  }

  get content() {
    return `side modal content ${this.constructor.name}`;
  }

  // header props by default use getter and setter — that enables us to override only getter, or just make
  // headerProps = {somestaticobject}
  // assignment

  simpleHeaderPropsData = {
    messageId: "(empty)"
  };

  get headerProps() {
    return this.simpleHeaderPropsData;
  }

  set headerProps(value) {
    this.simpleHeaderPropsData = value;
  }

  dataTestId = "smodal_default";

  contentPadding = 2;

  destroy() {
    this.payload = undefined;
    this.closeSideModal = undefined;
  }
}

export default BaseSideModal;
