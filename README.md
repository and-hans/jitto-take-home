# Jitto Full Stack Engineering Internship Take-Home Challenge

## 1. Overview of DynamoDB Schema

#### Schema Design:
- Partition Key: Performer [String]
- Sort Key: Date-Stage [String]
- Attributes:
    - Non Key: Start [String]
    - Non Key: End [String]

The partition is set to the Performers as it will generally be the unique value, making it efficient to query it as the partition. This supports the "retrieve all performances by a specific performer" requirement.

The sort key is set as Date-Stage allowing for the support of the "fetch details for a specific performance given a stage and time" requirement.

In order to meet the "list all performances occurring within a given time range" efficient querying, a Global Secondary Index (GSI) is needed in which the schema defined would be:
- Partition Key: Date [String]
- Sort Key: Start [String]

#### Summary Table:

| Query                                        | Schema Support                 | Efficiency                                  |
|----------------------------------------------|--------------------------------|---------------------------------------------|
| Retrieve all performances by a performer     | Partition Key                  | High (constant time)                        |
| List all performances in a time range        | Requires GSI on Date and Start | Efficient with GSI (avoids full table scan) |
| Fetch details for a performance (stage/time) | Supported but uses filtering   | Moderate (due to filtering)                 |

## 2. Cost and Scalability Analysis

#### Cost Analysis:

100 lines of CSV data, in the same format as "Music Festival Example Data - Sheet1.csv", is 5 kB.
- 1,000 daily records = 50 kB/day
- 10,000 daily records = 500 kB/day
- 100,000 daily records = 5 MB/day

Assumptions:
- Data Size: Each file is 5 MB, containing 100,000 rows
- Data Uploads: 1 file per day, totaling 30 files per month
- DynamoDB Storage: Each row is approximately 300 bytes, totaling 30 MB for all rows in a month
- Query Volume: 1,000 queries per day, totaling 30,000 queries per month
- Lambda Executions: Lambda is triggered once per file upload, running 30 times per month
- SNS Notifications: SNS sends one notification per Lambda execution, totaling 30 notifications per month

S3 Cost Table:
| Component    | Calculation                             | Monthly Cost                             |
|--------------|-----------------------------------------|------------------------------------------|
| Storage      | 30 files * 5MB = 150MB                  | 150MB * 0.023 \$/GB = $0.00345            |
| PUT Requests | 30 requests                             | 30 * 0.005 \$/1,000 requests = $0.00015   |
| GET Requests | 30 files * 10 reads/file = 300 requests | 300 * 0.0004 \$/1,000 requests = $0.00012 |
| Total        |                                         | $0.004                                   |

DynamoDB Cost Table:
| Component      | Calculation                                        | Monthly Cost                           |
|----------------|----------------------------------------------------|----------------------------------------|
| Storage        | 100,000 rows/file * 30 files * 300 bytes/row = 9MB | 9MB * 0.25 \$/GB = $0.00225             |
| Read Requests  | 100,000 rows/file * 30 files = 3,000,000 writes    | 3,000,000 * 0.00000125 \$/write = $3.75 |
| Write Requests | 30,000 queries/month                               | 30,000 * 0.000000625 \$/read = $0.01875 |
| Total          |                                                    | $3.77                                  |

Lambda Cost Table:
| Component      | Calculation                                                      | Monthly Cost |
|----------------|------------------------------------------------------------------|--------------|
| Execution Time | 30 invocations * 5 seconds/invocation * 128MB = 19,200MB-seconds | ---          |
| Cost           | 19,200MB-seconds * 0.00001667 \$/MB-second                        | $0.32        |
| Request Cost   | 30 requests/month * 0.20 \$/million requests                      | $0.000006    |
| Total          |                                                                  | $0.320006    |

SNS Cost Table:
| Component          | Calculation                                      | Monthly Cost |
|--------------------|--------------------------------------------------|--------------|
| Messages Published | 30 notifications/month * 0.50 $/million messages | $0.000015    |
| Total              |                                                  | $0.000015    |

Total = $4.09 per month

#### Scalability Analysis

- DynamoDB scales automatically for read and write capacity
- Lambda handles concurrent requests efficiently
