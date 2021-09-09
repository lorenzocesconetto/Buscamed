from app import create_app, db, scheduler, admin, cli, scrape, flaskadmin
from app.models import Item, Order, User, Store, Permission, Role
import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
cli.register(app)
scrape.register(app)
flaskadmin.register(admin, db)
scheduler.start()


@app.shell_context_processor  # Shell automatic imports
def make_shell_context():
    return {
        'db': db, 'User': User,
        'Item': Item, 'Role': Role, 'Order': Order,
        'Permission': Permission, 'Store': Store,
        'es': app.elasticsearch,
    }
