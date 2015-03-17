from collections import defaultdict
from flask.ext.sqlalchemy import SQLAlchemy

# Creating an 'app-like thing' that can be used with Flask-SQLAlchemy to
# avoid needing to instantiate the whole Flask stuff
# even though flask is lightweight and we love it

# Must support all the Flask-SQLAlchemy methods/properties that app supports


class SQLAlchemyConfig(object):
    config = defaultdict(lambda: False)
    root_path = ''
    debug = True

    def __init__(self, db_uri):
        self.import_name = __name__
        self.config['SQLALCHEMY_DATABASE_URI'] = db_uri
        self.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    def after_request(self, f):
        # teardown function, note, this is a decorator
        return f


class DB(SQLAlchemy):
    def __init__(self, db_uri):
        config = SQLAlchemyConfig(db_uri)
        super(DB, self).__init__(config)
