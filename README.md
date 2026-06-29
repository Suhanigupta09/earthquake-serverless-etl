# Earthquake Serverless ETL Pipeline

## Project Overview

This project implements a serverless ETL pipeline using Amazon S3, AWS Lambda, Amazon DynamoDB, GitHub Actions, AWS CodeBuild, and AWS CodePipeline.

The pipeline processes earthquake data stored as a CSV file. Invalid records are rejected, valid records are cleaned and transformed, and the final records are stored in DynamoDB.

## Dataset Source

The project uses a sample earthquake dataset inspired by public earthquake datasets such as the USGS earthquake feed.

The dataset contains:

* Earthquake ID
* Place
* Magnitude
* Depth
* Event time
* Latitude
* Longitude

## ETL Scenario

The use case is to prepare clean earthquake records for analytics, monitoring, or alerting.

Raw earthquake data is uploaded to the `raw/` prefix in Amazon S3. The upload automatically triggers an AWS Lambda function.

The Lambda function reads the CSV file, validates and transforms the records, and stores clean data in Amazon DynamoDB.

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

## ETL Rules

### Extract

The Lambda function reads the CSV file from:

```text
s3://suhani-earthquake-etl-2026/raw/sample_raw_data.csv
```

### Transform

The Lambda function applies the following rules:

1. Removes records with a missing earthquake ID.
2. Removes records with a missing place.
3. Removes records with a negative magnitude.
4. Standardizes the place field using title case.
5. Converts magnitude, depth, latitude, and longitude into numeric values.
6. Adds a derived `severity` field.

Severity rules:

* Magnitude greater than or equal to 6: High
* Magnitude greater than or equal to 4: Medium
* Magnitude below 4: Low

The function also adds a `processed_at` timestamp.

### Load

The clean records are written to the DynamoDB table:

```text
clean_records
```

## DynamoDB Table Design

* Table name: `clean_records`
* Partition key: `record_id`
* Partition key type: String
* Capacity mode: On-demand

The `record_id` field uniquely identifies each earthquake record.

## Audit Logging

The Lambda function writes an audit summary to Amazon CloudWatch Logs.

The audit summary includes:

* Total input records
* Inserted records
* Rejected records
* Processing timestamp

Test result:

```text
Total input records: 6
Inserted records: 4
Rejected records: 2
```

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
4. Validates the Lambda Python syntax using:

```bash
python -m py_compile lambda_function.py
```

## AWS CodePipeline

The AWS CodePipeline contains these stages:

```text
Source → Build → Deploy
```

### Source Stage

The Source stage reads the project from the GitHub repository and the `main` branch.

### Build Stage

AWS CodeBuild uses `buildspec.yml` to:

* Install Python dependencies
* Validate Lambda syntax
* Generate the build artifact

### Deploy Stage

The Deploy stage updates the existing AWS Lambda function:

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
├── sample_data/
│   └── sample_raw_data.csv
├── screenshots/
├── .gitignore
├── README.md
├── buildspec.yml
├── lambda_function.py
└── requirements.txt
```

## Security

The project does not store AWS access keys, secret keys, `.env` files, credentials, zip files, or generated package folders in GitHub.

The S3 bucket blocks public access.

IAM permissions are attached to the Lambda execution role to allow S3 reading, DynamoDB writing, and CloudWatch logging.

## Final Result

The project successfully demonstrates a working serverless ETL pipeline with:

* Raw earthquake data stored in Amazon S3
* Automatic Lambda processing
* Invalid record removal
* Clean DynamoDB records
* CloudWatch audit logs
* GitHub version control
* Successful GitHub Actions validation
* Successful AWS CodePipeline build and Lambda deployment
