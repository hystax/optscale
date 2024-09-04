### **Summary**

Use this page to visualize and access task data for analysis, creating leaderboards, tracking model versions, 
and getting recommendations.

### **View**

- Performance Management Toolbar: Use the Page toolbar with the "Refresh", "Profiling Integration", and "Configure" buttons.

- Summary Cards: Get an overview of the last run status, last run duration, lifetime cost, and potential summary savings 
  for each task.

- Tabs: View detailed information about training data by switching between the corresponding tabs.

### **Actions**

- Configure a Task: Use the "Configure" button to change the default task parameters, set up metrics, and configure a 
  leaderboard template.

- Manage Your Task: Click on the tab to get the data

  - Overview: Monitor task details and latest run information.
  
  - Runs: Analyze data on task runs in a graphical and table representation. Monitor selected metrics according to the 
    Category selected in the Filter on the runs chart. Review the status, metrics, hyperparameters, dataset, expenses, and 
    additional details for each run into the runs table. If the run has met all the metrics goals, it will be highlighted 
    with a green line on the left. Click on the name of the run for detailed information.

  - Model Version: View versions of models that were created in task runs.

  - Leaderboards: Compare groups of task runs (candidates) that are grouped by hyperparameters and tags to obtain optimal 
    launch parameters. Easily create a new leaderboard by clicking the "+" button (by default, the leaderboard is created 
    based on the leaderboard template). Specify the signs of grouping runs into groups, qualification protocol, and 
    datasets coverage rules. When a new run is added, the leaderboards are recalculated automatically! Get information 
    about candidates by clicking on a line in the leaderboard table. Find leaders and worthy candidates!

  - Recommendations: View recommendations for cloud instances that were used during training. Recommendations are active
    for instances that have been used in the last 7 days.

  - Executors: Check executors on which training code was executed. 

### **Tips**

- Experiment Tracking: Runs allow you to log and track different parameters, metrics, and artifacts associated with your
  machine learning experiments. This helps in keeping a detailed record of what was done during each experiment.

- Performance Comparison: Leaderboards provide a structured way to compare the performance of different models or 
  approaches on a common task or dataset. This helps in identifying which methods are more effective.
