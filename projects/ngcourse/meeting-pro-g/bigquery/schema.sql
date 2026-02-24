CREATE OR REPLACE TABLE `meetingprog.requests_table` (
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
    user_email STRING NOT NULL,
    thread_id STRING,
    intent_classification STRING,
    status STRING,
    metadata JSON
)
PARTITION BY DATE(timestamp);