import { removeKey } from "./objects";

class RequestManager {
  constructor() {
    this.pendingRequests = {};
    this.affectedRequests = {};
  }

  addAffectedRequest = (effectSourceLabel, affectedLabels) => {
    affectedLabels.forEach((affectedLabel) => {
      const labelsSet = this.affectedRequests[effectSourceLabel] || new Set();
      this.affectedRequests[effectSourceLabel] = labelsSet.add(affectedLabel);
    });
  };

  getAffectedRequests = (apiLabel) => this.affectedRequests[apiLabel] || [];

  addPendingRequest = (requestId, label) => {
    const abortController = new AbortController();

    this.pendingRequests[requestId] = {
      abortController,
      label
    };

    return abortController.signal;
  };

  hasPendingRequest = (label) => Object.values(this.pendingRequests).some((request) => request.label === label);

  removePendingRequest = (requestId) => {
    this.pendingRequests = removeKey(this.pendingRequests, requestId);
  };

  cancelPendingRequest = (requestId) => {
    this.pendingRequests[requestId].abortController.abort();
    this.removePendingRequest(requestId);
  };

  cancelPreviousPendingRequests = (label) => {
    Object.entries(this.pendingRequests).forEach(([requestId, request]) => {
      if (request.label === label) {
        this.cancelPendingRequest(requestId);
      }
    });
  };

  cancelAllPendingRequests = () => {
    Object.keys(this.pendingRequests).forEach((requestId) => {
      this.cancelPendingRequest(requestId);
    });
  };
}

export default new RequestManager();
