Hystax has been developing OptScale, an MLOps & FinOps open source platform. The software is fully available as a free source code on the [GitHub page](https://github.com/hystax/optscale) for download and deployment. OptScale aims to monitor and optimize cloud expenses, performance, and cloud and machine learning operations by analyzing cloud usage, profiling, and application instrumentation and providing valuable recommendations for optimization. Moreover, the MLOps capabilities of OptScale enable ML/AI teams by offering features for experiment tracking, hyperparameter tuning, performance optimization, and cost management, contributing to more streamlined and cost-effective compute operations.

The how-to article below will show how OptScale enhances RI/SP utilization by ML/AI teams in practice.

# How to use OptScale to optimize RI/SP usage for ML/AI teams


<p align="center">
<img src="documentation/images/Databricks-account-support.png" width="40%" align="middle">
</p>
Hystax is excited to announce Databricks cost management within the OptScale MLOps platform.
<br>
<br>
Responding to customers’ feedback and committed to enhancing cloud usage efficiency, we have recognized the importance of including Databricks expense tracking and visibility in OptScale. This functionality provides a detailed and controlled approach to managing Databricks costs.

## Feature overview
Supporting Databricks in the Hystax OptScale platform is designed to improve visibility and control over Databricks expenses and give details on which experiments the costs are distributed (or how the Databricks costs are distributed across ML experiments and tasks). Here's a brief overview of the key functionalities:

- Unified experience: The connected Databricks data source is managed like other data sources.
- Cost allocation: OptScale captures metadata from Databricks resources, such as name, tags, and region, enabling effective cost allocation.
- Custom pricing support: If your organization has a custom agreement with Databricks and uses custom rates for Databricks services, these can be reflected in the connection properties. This alignment ensures the expenses shown in OptScale match your final bill.
