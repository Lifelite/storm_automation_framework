import enum

from google.cloud import bigtable
from google.cloud.bigtable.row_set import RowSet

############ BE CAREFUL, You are charged per API call, don't cost yourself tons of money because of a recursion.

class BigTable:
    """
    Gets client and project information and allows for Queries to be run on BigTable for the requested project.

    :type   project_id:             str
    :param  project_id:             The Google Cloud BigTable Project id.

    :type   instance_id:            str
    :param  instance_id:            UID of the BigTable instance to be interacted with.

    :type   table_id:               str
    :param  table_id:               The BigTable table id.

    """
    def __init__(
            self,
            project_id,
            instance_id = None,
            table_id = None,
    ):
        self.project_id = project_id
        self.last_result = []
        self.instance_id = instance_id
        self.table_id = table_id

        self.client = bigtable.Client(project=self.project_id)

        # Connect to an existing Cloud BigTable instance.
        instance = self.client.instance(instance_id)

        # Open an existing table.
        self.table = instance.table(table_id)

    def read_row_keys(self, keys: list or str):
        """
        Overall function for retrieving rows from BigQuery table using row key(s).  Can accept single row key as
        string or can accept a list of row keys.

        :param  keys:                   String of a single row key or a list of row keys
        :type   keys:                   list or str
        :return:                        Result from row key lookup on BigTable.
        """

        if isinstance(keys, str) or len(keys) == 1:
            if isinstance(keys, list):
                return self.table.read_row(keys[0])
            return self.table.read_row(keys)

        row_set = RowSet()
        rows = []
        for key in keys:
            row_set.add_row_key(key)
        result_iter = iter(self.table.read_rows(row_set=row_set))
        for row in result_iter:
            rows.append(row)
        return rows

    # def read_rows_in_time_range(self, start_time: datetime, end_time: datetime = None):
    #     """
    #     Used for querying all rows that were created/updated within a time range.
    #     ***UNTESTED***
    #
    #     :param start_time:
    #     :param end_time:
    #     :return:
    #     """
    #     row_filters = RowFilter()
    #     return self.table.read_rows(
    #         filter_=row_filters.(row_filters.TimestampRange(start_time, end_time))
    #     )

    def read_rows_with_prefix(self, prefix):
        """
        Query BigTable for rows matching provided prefix.
        :param  prefix:                   String of prefix.
        :type   prefix:                   str

        :return:                          List of rows returned from Query that match provided prefix.
        :rtype:                           list
        """
        rows = []
        row_set = RowSet()
        row_set.add_row_range_with_prefix(prefix)
        result_iter = iter(self.table.read_rows(row_set=row_set))

        for row in result_iter:
            rows.append(row)
        return rows

    #
    # def read_rows_with_regex(self, regex_value):
    #     """
    #     Used for retrieving all the rows that pass the regex filter supplied.
    #
    #     :param regex_value:                     Regular expression filter.
    #     :type  regex_value:                     str
    #     :return:
    #     """
    #
    #     return self.table.read_rows(filter_=row_filters.RowKeyRegexFilter(regex_value.encode('utf-8')))

    #TODO: Create data helper function to return data in a more friendly format.

    # def convert_row_data_to_dict(self, data: RowSet):
    #     """
    #     Helper function for getting values for a specific column in a row returned from BigTable.read_rows.  Returns
    #     as an array of cell values.
    #
    #     :param  column_name:                Name of the column whose values should be returned
    #     :type   column_name:                str
    #
    #     :param  data:                       Data returned from BigTable.read_rows
    #     :type   data:                       RowSet
    #
    #     :return dict:                       Returns array of values from column.
    #     :exception:                         Column not found.
    #     """
    #     cells = data.cells
    #     column = None
    #     try:
    #         column = dict(cells[column_name])
    #     except ValueError:
    #         raise Exception("Column was not found")
    #     result = dict()
    #     for item in column:
    #         result[item.decode('utf-8')] = column[item]
    #     statuses = []
    #     for item in result[column_name]:
    #         statuses.append(item.value.decode('utf-8'))
    #     return statuses

# class BigTableRow(enum.Enum):
