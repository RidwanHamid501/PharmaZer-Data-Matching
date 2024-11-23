'''Pharmazer pipeline - etl script'''
from os import environ as ENV
from dotenv import load_dotenv
from extract import main as download_file, get_aws_session
from transform import main as process_data
from load import main as load_data


# def verify_email_identity(client):
#     '''Verify identity'''
#     client.verify_email_identity(
#         EmailAddress=ENV['EMAIL']
#     )


def send_email(client, message):
    '''Send start and ending emails'''

    response = client.send_email(
        Source=ENV['EMAIL'],
        Destination={
            'ToAddresses': [ENV['EMAIL']]
        },
        Message={
            'Subject': {
                'Data': 'File processing'
            },
            'Body': {
                'Text': {
                    'Data': message
                }
            }
        }
    )
    return response


def run_etl():
    '''Download, process and upload file from and into given s3 buckets'''
    load_dotenv()
    session = get_aws_session()
    client = session.client('ses')
    # verify_email_identity(client)
    send_email(client, 'Process Started')
    file = download_file()
    data = process_data(file)
    load_data(data)
    send_email(client, 'Process Finished')


if __name__ == "__main__":
    run_etl()
