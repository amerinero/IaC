import argparse
import datetime

# [START build_service]
from google.cloud import datastore

def create_client(project_id):
    return datastore.Client(project_id)
# [END build_service]

# [START add_entity]
def add_task(client, description):
    key = client.key('Task')

    task = datastore.Entity(
        key, exclude_from_indexes=['description'])

    task.update({
        'created': datetime.datetime.utcnow(),
        'description': description,
        'done': False
    })
