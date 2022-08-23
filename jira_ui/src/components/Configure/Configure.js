import React from "react";
import ConnectToOptscaleSection from "components/ConnectToOptscaleSection";
import OrganizationAssignmentSection from "components/OrganizationAssignmentSection";

const Configure = ({ isConnected, refresh }) => (
  <>
    <div style={{ marginBottom: "32px" }}>
      <ConnectToOptscaleSection onSuccessLogin={() => refresh()} onSuccessLogout={() => refresh()} isConnected={isConnected} />
    </div>
    {isConnected && (
      <div>
        <OrganizationAssignmentSection />
      </div>
    )}
  </>
);

export default Configure;
