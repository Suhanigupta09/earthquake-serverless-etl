import boto3
import csv
import io
import json
from datetime import datetime , timezone
from decimal import Decimal

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = "clean_records"
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event, context):
    try:
        # Get bucket name and file name from S3 event
        bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
        object_key = event["Records"][0]["s3"]["object"]["key"]

        print(f"Reading file from bucket: {bucket_name}")
        print(f"File name: {object_key}")

        # Read CSV file from S3
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )

        file_content = response["Body"].read().decode("utf-8")
        csv_reader = csv.DictReader(io.StringIO(file_content))

        total_records = 0
        inserted_records = 0
        rejected_records = 0

        for row in csv_reader:
            total_records += 1

            try:
                record_id = row["id"].strip()
                place = row["place"].strip().title()
                magnitude = float(row["magnitude"])
                depth = float(row["depth"])
                event_time = row["event_time"].strip()
                latitude = float(row["latitude"])
                longitude = float(row["longitude"])

                # Remove invalid records
                if not record_id or not place:
                    rejected_records += 1
                    print(f"Rejected record: {row}")
                    continue

                if magnitude < 0:
                    rejected_records += 1
                    print(f"Rejected record: {row}")
                    continue

                # Derived field
                if magnitude >= 6:
                    severity = "High"
                elif magnitude >= 4:
                    severity = "Medium"
                else:
                    severity = "Low"

                clean_record = {
                    "record_id": record_id,
                    "place": place,
                    "magnitude": Decimal(str(magnitude)),
                    "depth": Decimal(str(depth)),
                    "event_time": event_time,
                    "latitude": Decimal(str(latitude)),
                    "longitude": Decimal(str(longitude)),
                    "severity": severity,
                    "processed_at": datetime.now(timezone.utc).isoformat()
                }

                table.put_item(Item=clean_record)
                inserted_records += 1

            except Exception as record_error:
                rejected_records += 1
                print(f"Record error: {record_error}")
                print(f"Rejected record: {row}")

        audit_summary = {
            "total_input_records": total_records,
            "inserted_records": inserted_records,
            "rejected_records": rejected_records,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        print("Audit Summary:")
        print(json.dumps(audit_summary))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "ETL completed successfully",
                "audit": audit_summary
            })
        }

    except Exception as error:
        print(f"Lambda error: {error}")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "ETL failed",
                "error": str(error)
            })
        }