import persistent
import transaction
import ZODB
import os

from app.config import config


class PersistentNodeCollection:
    # ToDO: Prepare nodes to be stored, or prepare nodes after loaded.
    pass


class PersistentStorage:
    def __init__(self):
        db_path = config.settings_path
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        zodb_filename = os.path.join(db_path, config.strings.zodb_filename)
        self.db = ZODB.DB(zodb_filename)
        self.connection = self.db.open()
        self.root = self.connection.root()

    def commit(self):
        transaction.commit()

persistent_storage = PersistentStorage()


class PersistentObject(persistent.Persistent):
    @staticmethod
    def commit_transaction():
        transaction.commit()