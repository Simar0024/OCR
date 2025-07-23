import azure.functions as func
import logging
import os
import json
import time
import smtplib
from email.message import EmailMessage
from azure.storage.blob import BlobServiceClient
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from io import BytesIO

app = func.FunctionApp()

BLOB_STRING     = os.environ["BLOB_CONNECTION_STRING"]
KEY             = os.environ["VISION_KEY"]
ENDPOINT        = os.environ["VISION_ENDPOINT"]
INPUT           = os.environ["INPUT_CONTAINER"]
OUTPUT          = os.environ["OUTPUT_CONTAINER"]
SENDER          = os.environ["SENDER"]
RECEIVER        = os.environ["RECEIVER"]
PASSWORD        = os.environ["PASSWORD"]

blob_service_client = BlobServiceClient.from_connection_string(BLOB_STRING)
computervision_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))


@app.blob_trigger(arg_name="myblob", path="input/{name}",
                  connection="ocr01storage_STORAGE")
def blob_trigger_ocr(myblob: func.InputStream):
    blob_name = myblob.name.split("/")[-1]
    logging.info(f"[Trigger] Blob detected: {blob_name} ({myblob.length} bytes)")
    
    try:
        result = extract_text(blob_name)
        output_file = upload_json(blob_name, result)
        send_email(output_file)
        logging.info(f"[Success] OCR complete and JSON uploaded: {output_file}")
    except Exception as e:
        logging.error(f"[Error] Failed to process blob: {blob_name}")
        logging.error(str(e))


def extract_text(blob_name):
    logging.info(f"[OCR] Extracting text from: {blob_name}")
    blob_client = blob_service_client.get_blob_client(INPUT, blob_name)
    image_data = blob_client.download_blob().readall()

    response = computervision_client.read_in_stream(BytesIO(image_data), raw=True)
    operation_id = response.headers["Operation-Location"].split("/")[-1]

    while True:
        result = computervision_client.get_read_result(operation_id)
        if result.status not in ['notStarted', 'running']:
            break
        time.sleep(1)

    lines = []
    if result.status == OperationStatusCodes.succeeded:
        for page in result.analyze_result.read_results:
            for line in page.lines:
                lines.append(line.text)

    return {
        "filename": blob_name,
        "lines": lines
    }


def upload_json(blob_name, data):
    logging.info(f"[Upload] Uploading result for: {blob_name}")
    out_name = os.path.splitext(blob_name)[0] + ".json"
    blob_client = blob_service_client.get_blob_client(OUTPUT, out_name)
    blob_client.upload_blob(json.dumps(data, indent=2).encode('utf-8'), overwrite=True)
    return out_name

def send_email(output_file):
    try:
        logging.info(f"[Email] Sending notification for: {output_file}")
        msg = EmailMessage()
        msg["Subject"] = "OCR Output Ready"
        msg["From"] = SENDER
        msg["To"] = RECEIVER
        msg.set_content(f"The OCR result has been uploaded: {output_file}")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER, PASSWORD)
            smtp.send_message(msg)

        logging.info(f"[Email] Sent successfully to {RECEIVER}!")
        
    except Exception as e:
        logging.error(f"[Email Error] Failed to send email for {output_file}!")
        logging.error(str(e))
