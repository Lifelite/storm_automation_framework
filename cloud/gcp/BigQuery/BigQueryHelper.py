import logging
import os
from google.cloud import bigquery

class BigQueryHelper:
    def __init__(self, project_id, auth_through_gcloud_cli=True ):
        self.credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if self.credentials is None and not auth_through_gcloud_cli:
            raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set")
        self.bq_client = None

    def connect(self):
        self.bq_client = bigquery.Client()

    def close(self):
        if self.bq_client:
            self.bq_client.close()
        else:
            logging.log(logging.WARN, "No client connected, client close has no effect.")

    # def query(self, ):
    #
