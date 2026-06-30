import csv
import io
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

TABLE_NAME = "clean_records"
table = dynamodb.Table(TABLE_NAME)


def get_severity(magnitude):
    if magnitude >= 6:
        return "High"

    if magnitude >= 4:
        return "Medium"

    return "Low"


def clean_record(row):
    try:
        record_id = str(row.get("id", "")).strip()
        place = str(row.get("place", "")).strip().title()
        event_time = str(row.get("event_time", "")).strip()

        magnitude = float(row.get("magnitude", ""))
        depth = float(row.get("depth", ""))
        latitude = float(row.get("latitude", ""))
        longitude = float(row.get("longitude", ""))

        if not record_id:
            return None, "Missing earthquake ID"

        if not place:
            return None, "Missing place"

        if magnitude < 0:
            return None, "Negative magnitude"

        item = {
            "record_id": record_id,
            "place": place,
            "magnitude": Decimal(str(magnitude)),
            "depth": Decimal(str(depth)),
            "event_time": event_time,
            "latitude": Decimal(str(latitude)),
            "longitude": Decimal(str(longitude)),
            "severity": get_severity(magnitude),
            "source_file_type": "CSV",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }

        return item, None

    except (ValueError, TypeError) as error:
        return None, f"Invalid numeric value: {error}"


def lambda_handler(event, context):
    try:
        logger.info("CSV processor started")
        logger.info("Received event: %s", json.dumps(event))

        bucket_name = event["bucket"]
        object_key = event["key"]

        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=object_key
        )

        content = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))
        records = list(reader)

        total_records = len(records)
        inserted_records = 0
        rejected_records = 0

        for row in records:
            clean_item, rejection_reason = clean_record(row)

            if clean_item is None:
                rejected_records += 1
                logger.warning(
                    "Rejected record %s: %s",
                    row,
                    rejection_reason
                )
                continue

            table.put_item(Item=clean_item)
            inserted_records += 1

        audit_summary = {
            "parser": "CSV",
            "source_file": object_key,
            "total_input_records": total_records,
            "inserted_records": inserted_records,
            "rejected_records": rejected_records,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.info("CSV Audit Summary: %s", json.dumps(audit_summary))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "CSV ETL completed successfully",
                "audit": audit_summary
            })
        }

    except Exception as error:
        logger.exception("CSV processor failed")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "CSV ETL failed",
                "error": str(error)
            })
        }