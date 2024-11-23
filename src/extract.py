'''Download file from s3 bucket'''
from os import environ as ENV
import boto3
from dotenv import load_dotenv


def get_aws_session() -> boto3.Session:
    """Create and return AWS session"""
    return boto3.Session(
        aws_access_key_id=ENV['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=ENV['AWS_SECRET_ACCESS_KEY']
    )


def get_files_in_bucket(client: boto3.client, bucket_name: str) -> list[dict]:
    """Fetch all file objects in the specified S3 bucket"""
    prefix = ENV["FILE_NAME"]
    bucket_objects = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return bucket_objects.get('Contents', [])


def get_last_modified_file_name(files):
    '''Fetch file with latest modified time'''
    return max(files, key=lambda file: file['LastModified'])['Key']


def download_file(client, file, bucket_name):
    '''Download the file locally'''
    client.download_file(
        bucket_name, file, file)


def main() -> None:
    '''Main function to download the file and return file name'''
    load_dotenv()
    session = get_aws_session()
    client = session.client('s3')

    bucket_name = ENV['BUCKET_NAME']

    bucket_files = get_files_in_bucket(client, bucket_name)

    file_name = get_last_modified_file_name(bucket_files)

    download_file(client, file_name, bucket_name)

    print(file_name)

    return file_name


if __name__ == "__main__":
    main()
