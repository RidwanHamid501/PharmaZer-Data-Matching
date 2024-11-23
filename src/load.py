'''Script to upload transformed data as a csv into the output s3 bucket'''
import logging
import os
from os import environ as ENV
from dotenv import load_dotenv
from extract import get_aws_session
import transform


def save_to_csv(file_name, data):
    '''Save dataframe to csv'''
    data.to_csv(file_name, index=False)


def save_to_bucket(client, processed_file_name, bucket_name):
    '''Upload csv file to output s3 bucket'''
    client.upload_file(processed_file_name, bucket_name, processed_file_name)


def delete_files(client, bucket_name, file_name):
    '''Delete file in input s3 and files downloaded locally'''
    client.delete_object(Bucket=bucket_name, Key=file_name)
    os.remove("processed-data.csv")
    os.remove(file_name)


def main(data):
    '''Main function to upload csv file to output s3 bucket'''
    load_dotenv()

    processed_file_name = "processed-data.csv"
    bucket_name_out = ENV["BUCKET_NAME_OUT"]
    bucket_name_in = ENV["BUCKET_NAME"]
    file_name = ENV["FILE_NAME"]

    session = get_aws_session()
    client = session.client("s3")

    logging.info("Saving results to %s...", processed_file_name)

    save_to_csv(processed_file_name, data)
    save_to_bucket(client, processed_file_name, bucket_name_out)

    logging.info("Processing complete.")

    delete_files(client, bucket_name_in, file_name)


if __name__ == "__main__":
    load_dotenv()
    file = ENV["FILE_NAME"]
    df = transform.main(file)
    main(df)
