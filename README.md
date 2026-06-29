# Earthquake Serverless ETL Pipeline

## Project Overview

This project implements a serverless ETL pipeline using Amazon S3, AWS Lambda, Amazon DynamoDB, Amazon CloudWatch, GitHub Actions, AWS CodeBuild, and AWS CodePipeline.

The pipeline processes earthquake data stored in a CSV file. Invalid records are rejected, valid records are cleaned and transformed, and the final records are stored in DynamoDB.

## Dataset Source

This project uses a sample earthquake CSV dataset created for this assignment and inspired by public USGS earthquake datasets.

The dataset contains the following fields:

* Earthquake ID
* Place
* Magnitude
* Depth
* Event time
* Latitude
* Longitude

## ETL Scenario

The purpose of this project is to prepare clean earthquake records for analytics, monitoring, or alerting.

The raw earthquake CSV file is uploaded to the `raw/` prefix in Amazon S3. The upload triggers an AWS Lambda function.

The Lambda function reads the file, validates the records, transforms the valid records, and stores the clean data in Amazon DynamoDB.

## Architecture

```text
Earthquake CSV Data
        |
        v
Amazon S3 raw/
        |
        v
AWS Lambda ETL Function
        |
        v
Amazon DynamoDB clean_records
        |
        v
Amazon CloudWatch Logs

GitHub Repository
        |
        v
GitHub Actions
        |
        v
AWS CodePipeline
        |
        v
AWS CodeBuild
        |
        v
AWS Lambda Deployment
```

## AWS Services Used

* Amazon S3
* AWS Lambda
* Amazon DynamoDB
* Amazon CloudWatch
* AWS Identity and Access Management
* AWS CodeBuild
* AWS CodePipeline

## ETL Process

### Extract

The Lambda function reads the CSV file from:

```text
s3://suhani-earthquake-etl-2026/raw/sample_raw_data.csv
```

### Transform

The Lambda function applies the following transformation rules:

1. Removes records with a missing earthquake ID.
2. Removes records with a missing place.
3. Removes records with a negative magnitude.
4. Standardizes the place field using title case.
5. Converts magnitude, depth, latitude, and longitude into numeric values.
6. Adds a derived `severity` field.
7. Adds a `processed_at` timestamp.

### Severity Rules

* Magnitude greater than or equal to `6` → `High`
* Magnitude greater than or equal to `4` → `Medium`
* Magnitude below `4` → `Low`

### Load

The clean records are written to the DynamoDB table:

```text
clean_records
```

## DynamoDB Table Design

* Table name: `clean_records`
* Partition key: `record_id`
* Partition key type: `String`
* Capacity mode: `On-demand`

The `record_id` field uniquely identifies each earthquake record.

## Audit Logging

The Lambda function writes an audit summary to Amazon CloudWatch Logs.

The audit summary includes:

* Total input records
* Inserted records
* Rejected records
* Processing timestamp

### Test Result

```text
Total input records: 6
Inserted records: 4
Rejected records: 2
```

The following records were inserted:

```text
eq001
eq002
eq003
eq006
```

The following records were rejected:

```text
eq004 - Negative magnitude
eq005 - Missing place
```

## S3 Trigger

An S3 trigger is connected to the Lambda function.

Trigger settings:

* Bucket: `suhani-earthquake-etl-2026`
* Prefix: `raw/`
* Suffix: `.csv`
* Event type: `All object create events`

Whenever a CSV file is uploaded to the `raw/` prefix, the Lambda function runs automatically.

## Testing Steps

1. Upload `sample_raw_data.csv` to the S3 `raw/` prefix.
2. Confirm that S3 triggers the Lambda function.
3. Check the Lambda execution result.
4. Open CloudWatch Logs and verify the audit summary.
5. Open DynamoDB and scan the `clean_records` table.
6. Confirm that four clean records were inserted.

## GitHub Actions

The GitHub Actions workflow runs on every push and pull request.

It performs the following steps:

1. Checks out the repository.
2. Sets up Python 3.11.
3. Installs dependencies from `requirements.txt`.
4. Validates the Lambda syntax using:

```bash
python -m py_compile lambda_function.py
```

## AWS CodePipeline

The AWS CodePipeline contains the following stages:

```text
Source → Build → Deploy
```

### Source Stage

The Source stage reads the project from:

```text
Suhanigupta09/earthquake-serverless-etl
```

Branch:

```text
main
```

### Build Stage

AWS CodeBuild uses `buildspec.yml` to:

* Install dependencies
* Validate the Lambda syntax
* Create the build artifact

### Deploy Stage

The Deploy stage updates the existing Lambda function:

```text
earthquake-etl-function
```

## Repository Structure

```text
earthquake-serverless-etl/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── sample_data/
│   └── sample_raw_data.csv
│
├── screenshots/
│   ├── 01_s3_raw_file_upload.png
│   ├── 02_lambda_execution_success.png
│   ├── 03_dynamodb_clean_records.png
│   ├── 04_cloudwatch_audit_logs.png
│   ├── 05_github_actions_success.png
│   └── 06_codepipeline_success.png
│
├── .gitignore
├── README.md
├── buildspec.yml
├── lambda_function.py
└── requirements.txt
```

## Security

The project does not store:

* AWS access keys
* AWS secret keys
* Credentials
* `.env` files
* ZIP packages
* Generated dependency folders

The S3 bucket blocks public access.

For this beginner project, the following AWS-managed policies were used:

```text
AmazonS3ReadOnlyAccess
AmazonDynamoDBFullAccess
AWSLambdaBasicExecutionRole
```

In a production project, these should be replaced with a least-privilege custom IAM policy.

## Final Result

This project successfully demonstrates:

* Raw earthquake data stored in Amazon S3
* Automatic processing using AWS Lambda
* Invalid record removal
* Field standardization
* Derived severity field creation
* Clean records stored in DynamoDB
* Audit logs stored in CloudWatch
* GitHub version control
* Successful GitHub Actions validation
* Successful AWS CodeBuild execution
* Successful AWS CodePipeline deployment
