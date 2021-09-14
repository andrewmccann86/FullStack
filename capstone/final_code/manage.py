from flask_script import Manager
from flask_migrate import Migrate

from app import app
from models import db

migrate = Migrate(app, db)
manager = Manager(app)
db.init_app(app)
migrate.init_app(app, db)

manager.add_command('db')


if __name__ == '__main__':
    manager.run()