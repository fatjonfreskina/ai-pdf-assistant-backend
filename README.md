# Openai-pdf-assistant :robot:

Laveraging OpenAI's Assistant API to create a PDF assistant that can help you with your PDFs.

## Features :sparkles:

- [X] User authentication
- [X] Assistant creation and management
- [X] PDF upload
- [x] Ask questions about the PDFs
- [ ] Hanlde conversations

## Contribute :raised_hands:

Contributions are more than welcome using the ["fork and pull request"](https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project) workflow. Briefly:

1. Fork the project and clone it locally.
2. Create a new branch following the pattern `<placeholder>-issueNumber`. Where placeholders can be `develop`, `bugfix`, `documentation` only.
3. Make your changes and push them to your fork.
4. Create a pull request to the main branch.
5. Your pull request will be reviewed and merged.

## Installation :wrench:

1. Clone the repository
2. Create a `.env` file in the root directory with the following content:

```bash
OPENAI_API_KEY=<your_openai_api_key>
ENVIRONMENT=<development|production>
FLASK_SECRET_KEY=<flask_secret>     # You can generate this from the terminal (see below)
FLASK_DEBUG=<True|False>
FLASK_APP=main.py
FLASK_RUN_PORT=<port>
FLASK_SQLALCHEMY_DATABASE_URI=<database_uri>
FLASK_SQLALCHEMY_ECHO=<True|False>
FLASK_JWT_SECRET_KEY=<jwt_secret_key> # Generate this from flask shell (see below)
```

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment: `source venv/bin/activate` or `.\venv\Scripts\activate` on Windows
3. Install the requirements: `pip install -r requirements.txt`
4. Set the `FLASK_APP` environment variable: `cd src && <export|set> FLASK_APP=main.py`
5. Finally, run the application: `flask run`

### Local database setup (SQLAlchemy) :floppy_disk:

```bash
# Generate FLASK_SECRET_KEY
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Generate FLASK_JWT_SECRET_KEY
python -c 'import secrets; print(secrets.token_hex(12))'

# Setup the DB (SQLAlchemy)
flask shell
db # Access the SQLAlchemy database instance
from data.user_model import User
db.create_all()
```

## Flask shell useful commands :shell:

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
