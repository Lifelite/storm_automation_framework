from os import path

from google.cloud import storage
from google.cloud.exceptions import ClientError
from google.cloud.storage import transfer_manager


class GoogleBucket:

    """
    Gets client and project information and contains functions for interacting with Google Buckets on GCP

    :type bucket_name:              str
    :param bucket_name:             The name of the specific bucket you are looking to interact with

    :type project_id:               str
    :param project_id:              The name of the GCP project associated to the bucket

    :type credentials:              any
    :param credentials:             (optional) GCP Service Account Credentials

    :type local_directory_path:     str
    :param local_directory_path:    (optional) Local path to the folder containing the x9 files needing to be tested.

    """

    def __init__(
            self,
            bucket_name,
            project_id,
            credentials=None,
            local_directory_path = "test_files/"
    ):
        self.project: str = project_id
        self.client: storage.Client = storage.Client(project=self.project)
        self.bucket = self.client.bucket(bucket_name)
        self.get_bucket = self.client.get_bucket(bucket_name)
        self.credentials = credentials
        self.local_directory_path: str = local_directory_path


    def upload_blob(self, file_name):
        """
        Uploads a file to the bucket.  Logs an exception if the file already exists, and if there's an error uploading.

        :type file_name:                str
        :param file_name:               The name of the file to be uploaded.

        :return:                        Returns True if file was uploaded, False otherwise.
        :rtype:                         bool
        """
        blob = self.bucket.blob(file_name)

        try:

            generation_match_precondition = 0

            full_path = path.join(self.local_directory_path, file_name)

            blob.upload_from_filename(full_path, if_generation_match=generation_match_precondition)
            print("File {} uploaded".format(file_name))
            return True

        except Exception as e:
            print("Issue with uploading, commonly caused by file name already existing in the bucket" + str(e))
            return False

    def upload_many_blobs_with_transfer_manager(
            self,
            filenames,
            source_directory=None,
            workers=8
    ):
        """Upload every file in a list to a bucket, concurrently in a process pool.

        Each blob name is derived from the filename, not including the
        `source_directory` parameter. For complete control of the blob name for each
        file (and other aspects of individual blob metadata), use
        transfer_manager.upload_many() instead.

        :param filenames:               Name of files to be uploaded, as a list of strings or bytes objects
        :type filenames:                Any

        :param source_directory:        Path (string) to the directory containing the files to be uploaded
        :type source_directory:         str or None

        :param workers:                 Number of workers to upload each file into the bucket.
        :type workers:                  int or None

        :return:                        If the files upload successfully, returns True, otherwise False.
        :rtype:                         bool
        """

        if not source_directory:
            source_directory = self.local_directory_path

        results = transfer_manager.upload_many_from_filenames(
            self.bucket, filenames, source_directory=source_directory, max_workers=workers
        )

        for name, result in zip(filenames, results):
            # The results list is either `None` or an exception for each filename in
            # the input list, in order.

            if isinstance(result, Exception):
                print("Failed to upload {} due to exception: {}".format(name, result))
            else:
                print("Uploaded {} to {}.".format(name, self.bucket.name))
                return True

    def delete_object(self, object_name) -> bool:
        """
        Deletes a blob from the bucket.
        :param object_name:     Name of the object to be deleted from Google Storage Bucket (BE CAREFUL)
        :type object_name:      str
        :return:                True if successful, False otherwise
        :rtype:                 bool
        """
        try:
            self.get_bucket.delete_blob(object_name)

            print(f"Blob {object_name} deleted.")
            return True
        except ClientError as e:
            print("Unable to delete: " + str(e))