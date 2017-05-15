# Dashboard

I recommend always working with one file. That is, everyone should import the file [```dashboards.json```](dashboards.json) to Kibana. Then, if you add any new features export it and upload it again! Just make sure that everyone knows that you are currently working on it in order to avoid anyone overwriting your work! Thus, for precaution, you might upload the updated file as ```dashboards_feature1.json```

### Remark on the visualizations

It would be nice to show some of the visualizations for different intervals. However, Kibana works with a single time interval and I could not add visualizations with different time intervals into one dashboard.

I was thinking of the following three intervals:

* **Oldest date - 14th June 2015**: This is the time prior to announcing his candidacy
* **15th June 2015 - 18th January 2017**: Time until he became president
* **18th January 2017 - now: First days** of presidency

In particular it is interesting to look at the hourly distribution of his tweets along one day. It changes considerably between these three intervals.
