import { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { resetResources } from "reducers/resources/actionCreators";

const OrganizationChangeListener = ({ children }) => {
  const { organizationId } = useOrganizationInfo();
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(resetResources());
  }, [dispatch, organizationId]);

  return children;
};

OrganizationChangeListener.propTypes = {
  children: PropTypes.node.isRequired
};

export default OrganizationChangeListener;
