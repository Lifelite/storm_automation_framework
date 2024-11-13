############ BE CAREFUL, You are charged per API call, don't cost yourself tons of money because of a recursion.
import time
from datetime import datetime

from google.cloud import bigquery


class BigQuery:
    """
    Gets client and project information and allows for Queries to be run on BigQuery for the requested project.

    :type project_id:           _SpecialForm[str] | str
    :param project_id:          The Google Cloud Big Query Project id, usually stored in framework.gcp.endpoints

    :type test_query:           framework.gcp.sql_queries | str
    :param test_query:          your specified SQL query, which should be stored in
                                ProjectRoot/framework/gcp/sql_queries.py
    """

    def __init__(
            self,
            project_id,
            test_query=None,

    ):
        self.testQuery = test_query
        self.project_id = project_id
        self.last_result = []
        # load_dotenv("../.env")
        # big_query_creds = getenv("GOOGLE_BIGQUERY_API_KEY")

        self.client = bigquery.Client(project=self.project_id)

    def executeRawQuery(self) -> list[dict]:
        """
        Executes the provided Query on the project defined when initializing the class, then returns the results.

        :return:                Result of query as a list of dictionaries.
        :rtype:                 list[dict]
        """
        results = self.client.query_and_wait(self.testQuery)

        #  Reset last_result

        self.last_result = []
        for row in results:
            self.last_result.append(dict(row.items()))
        return self.last_result

    #TODO: Combine methods into one.

    def executeParameterizedQuery(self, params: list, timeout_minutes: int = 10) -> list[dict]:
        """
        Run a Query on BigQuery using predefined SQL with specified parameters.  Timeout is specified in minutes,
        with the default being 10 minutes.  The query will retry every 5 seconds till it receives rows or exceeds the
        timeout specified.

        :param  params:             List of parameters to be used in the SQL Query
        :type   params:             list

        :param  timeout_minutes:    Time in minutes for the query job to continue trying to find returned results.
                                    Default is 10 minutes.
        :type   timeout_minutes:    int

        :return:                    Result of query as a list of dictionaries.
        :rtype:                     list[dict]
        """
        final_params = []
        for item in params:

            try:
                test_for_date = bool(datetime.strptime(item, '%Y-%m-%d %H:%M:%S.%f'))
            except ValueError:
                test_for_date = False

            if test_for_date:
                final_params.append(
                    bigquery.ScalarQueryParameter(None, "TIMESTAMP", item)
                )
            elif type(item) == str:
                final_params.append(
                    bigquery.ScalarQueryParameter(None, "STRING", item)
                )
            elif type(item) == int:
                final_params.append(
                    bigquery.ScalarQueryParameter(None, "NUMERIC", item)
                )
            elif type(item) == bool:
                final_params.append(
                    bigquery.ScalarQueryParameter(None, "BOOL", item)
                )
            else:
                raise Exception("Invalid type provided to BigQuery query parameter.")

        qConfig = bigquery.QueryJobConfig(query_parameters=final_params)
        timeout_start = time.time()
        timeout = 60 * timeout_minutes

        results = None
        while time.time() < timeout_start + timeout:
            results = self.client.query_and_wait(self.testQuery, job_config=qConfig)
            if results.total_rows > 0:
                break
            else:
                time.sleep(5)
                continue

        #   Reset last_result
        self.last_result = []

        #   Add results to Class object and return

        for row in results:
            self.last_result.append(dict(row.items()))
        return self.last_result
