const cloudAccountsMock = {
  cloudAccounts: [
    {
      id: "AWS Europe",
      type: "AWS",
      name: "AWS Europe",
      resources: 27,
      spend: 5400,
      forecast: 9770
    },
    {
      id: "Azure",
      type: "Azure",
      name: "Azure",
      resources: 12,
      spend: 5870,
      forecast: 9090
    },
    {
      id: "AWS HQ",
      type: "AWS",
      name: "AWS HQ",
      resources: 48,
      spend: 8000,
      forecast: 12300
    },
    {
      id: "GCP",
      type: "GCP",
      name: "GCP",
      resources: 21,
      spend: 8160,
      forecast: 13810
    }
  ],
  billing: {
    this_month_total: "31510",
    this_month_forecast: "58670"
  }
};

export default cloudAccountsMock;
