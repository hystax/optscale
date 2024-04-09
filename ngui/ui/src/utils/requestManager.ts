import { removeKey } from "./objects";

type PendingRequest = {
  abortController: AbortController;
  label: string;
};

class RequestManager {
  private pendingRequests: { [requestId: string]: PendingRequest };

  private affectedRequests: { [effectSourceLabel: string]: Set<string> };

  constructor() {
    this.pendingRequests = {};
    this.affectedRequests = {};
  }

  addAffectedRequest = (effectSourceLabel: string, affectedLabels: string[]) => {
    affectedLabels.forEach((affectedLabel) => {
      const labelsSet = this.affectedRequests[effectSourceLabel] || new Set();
      this.affectedRequests[effectSourceLabel] = labelsSet.add(affectedLabel);
    });
  };

  getAffectedRequests = (apiLabel: string) => [...(this.affectedRequests[apiLabel] || [])];

  addPendingRequest = (requestId: string, label: string) => {
    const abortController = new AbortController();

    this.pendingRequests[requestId] = {
      abortController,
      label
    };

    return abortController.signal;
  };

  hasPendingRequest = (label: string) => Object.values(this.pendingRequests).some((request) => request.label === label);

  removePendingRequest = (requestId: string) => {
    this.pendingRequests = removeKey(this.pendingRequests, requestId);
  };

  cancelPendingRequest = (requestId: string) => {
    this.pendingRequests[requestId].abortController.abort();
    this.removePendingRequest(requestId);
  };

  cancelPreviousPendingRequests = (label: string) => {
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
