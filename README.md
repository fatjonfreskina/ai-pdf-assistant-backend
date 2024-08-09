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
