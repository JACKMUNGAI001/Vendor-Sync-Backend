from algoliasearch.search_client import SearchClient
from flask import current_app

class AlgoliaService:
    def __init__(self):
        self.client = SearchClient.create(
            current_app.config['ALGOLIA_APP_ID'],
            current_app.config['ALGOLIA_API_KEY']
        )
        self.index = self.client.init_index('vendorsync_index')

    def add_record(self, record):
        self.index.save_object(record).wait()

    def update_record(self, record):
        self.index.partial_update_object(record).wait()

    def delete_record(self, object_id):
                    self.index.delete_object(object_id).wait()
