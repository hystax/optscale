import PageContentDescription from "components/PageContentDescription";

const InformationWrapper = ({ children }) => (
  <>
    <PageContentDescription
      position="top"
      alertProps={{
        messageId: "recommendationsSettingsOutOfSyncMessage",
      }}
    />
    {children}
  </>
);

export default InformationWrapper;
