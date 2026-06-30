import json
import logging
from urllib.parse import unquote_plus

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

lambda_client = boto3.client("lambda")

CSV_LAMBDA = "earthquake-csv-processor"
JSON_LAMBDA = "earthquake-json-processor"

SUPPORTED_BUCKET = "suhani-earthquake-etl-2026"


def lambda_handler(event, context):
    try:
        logger.info("Router Lambda started")
        logger.info("Received event: %s", json.dumps(event))

        record = event["Records"][0]["s3"]

        bucket_name = record["bucket"]["name"]
        object_key = unquote_plus(record["object"]["key"])

        logger.info("Uploaded file: s3://%s/%s", bucket_name, object_key)

        # Bucket-based routing/validation
        if bucket_name != SUPPORTED_BUCKET:
            raise ValueError(f"Unsupported bucket: {bucket_name}")

        # Only process files inside raw/
        if not object_key.startswith("raw/"):
            raise ValueError("Only files inside raw/ are supported")

        payload = {
            "bucket": bucket_name,
            "key": object_key
        }

        lower_key = object_key.lower()

        # File-type-based routing
        if lower_key.endswith(".csv"):
            target_lambda = CSV_LAMBDA
            file_type = "CSV"

        elif lower_key.endswith(".json"):
            target_lambda = JSON_LAMBDA
            file_type = "JSON"

        else:
            logger.warning("Unsupported file type: %s", object_key)

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": "Unsupported file type",
                    "supported_types": [".csv", ".json"],
                    "file": object_key
                })
            }

        logger.info(
            "%s file detected. Invoking %s",
            file_type,
            target_lambda
        )

        response = lambda_client.invoke(
            FunctionName=target_lambda,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload).encode("utf-8")
        )

        downstream_response = json.loads(
            response["Payload"].read().decode("utf-8")
        )

        logger.info(
            "Processor response: %s",
            json.dumps(downstream_response)
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File routed successfully",
                "file_type": file_type,
                "routed_to": target_lambda,
                "file": object_key,
                "processor_response": downstream_response
            })
        }

    except Exception as error:
        logger.exception("Router Lambda failed")

        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Routing failed",
                "error": str(error)
            })
        }