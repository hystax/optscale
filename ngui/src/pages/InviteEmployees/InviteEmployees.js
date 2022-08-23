import React from "react";
import Protector from "components/Protector";
import InviteEmployeesContainer from "containers/InviteEmployeesContainer";

const InviteEmployees = () => (
  <Protector allowedActions={["MANAGE_INVITES"]}>
    <InviteEmployeesContainer />
  </Protector>
);

export default InviteEmployees;
