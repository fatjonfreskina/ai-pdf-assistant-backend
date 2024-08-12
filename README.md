# openai-pdf-assistant

## Installation

```bash
pip install -r requirements.txt
cd src
flask run
```

## Useful links

### SQLAlchemy

```bash
flask shell # to open a shell
db # to access the db object
from data.user_model import User
db.create_all()

# Generate FLASK_JWT_SECRET_KEY from flask shell
import secrects
secrets.token_hex(12)
```

More commands:

```bash
app             # Access the Flask application instance.
current_app     # Access the current active Flask application.
g               # Access the application’s context globals.
request         # Access the incoming request object (only available during a request).
session         # Access the user session data (only available during a request).

db                              # The SQLAlchemy database instance if you are using Flask-SQLAlchemy.
db.create_all()                 # Create all database tables defined in your models.
db.drop_all()                   # Drop all database tables.
db.session.add(instance)        # Add an instance to the database session.
db.session.commit()             # Commit the current transaction.
db.session.rollback()           # Roll back the current transaction.
db.session.query(Model).all()   # Query all records of a model.
db.session.delete(instance)     # Delete an instance from the database.

Model.query.all()                                   # Retrieve all records from the table associated with the model.
Model.query.filter_by(attribute=value).first()      # Query records with specific criteria.
Model.query.get(id)                                 # Retrieve a record by its primary key.
model_instance.save()                               # Save an instance (requires custom method in model).
model_instance.delete()                             # Delete an instance (requires custom method in model).

# Example
from data.user_model import User
user = User.query.filter_by(username='fatjonfreskina').first()
```
