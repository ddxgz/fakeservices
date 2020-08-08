import os
import glob
import asyncio

from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from azure.storage.filedatalake import DataLakeServiceClient

from fakeservices import config


def upload_dir_datalake(path: str, file_system_name: str = 'p4-data'):
    try:
        ser_cli = DataLakeServiceClient.from_connection_string(
            config.AZURE_STORAGE_CONNECTION_STRING)
        filesys_cli = ser_cli.get_file_system_client(
            file_system=file_system_name)
        dir_cli = filesys_cli.get_directory_client(path)

        csv_files = glob.glob(f'{path}/**/*.csv', recursive=True)
        for csv_f in csv_files:
            # afile = 'results/pi/common apis_1595417687.0704062.csv'
            file_cli = dir_cli.get_file_client(csv_f)
            with open(csv_f, 'r') as f:
                file_cli.upload_data(f.read(), overwrite=True)

    except Exception as e:
        print(e)


async def azure_send_event(events):
    producer = EventHubProducerClient.from_connection_string(
        conn_str=config.AZURE_EVENT_HUB_CONNECTION_STRING,
        eventhub_name=config.AZURE_EVENT_HUB_NAME)
    async with producer:
        event_data_batch = await producer.create_batch()

        for event in events:
            event_data_batch.add(EventData(event))

        await producer.send_batch(event_data_batch)


# upload_dir_datalake('results')

# loop = asyncio.get_event_loop()
# loop.run_until_complete(azure_send_event([{'a': 'a'}, {'B': 'B'}]))
