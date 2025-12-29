# feeshunofficial-com-django

A Wagtail-based Django project.

## Setup

1. Create a virtual environment:

   ```bash

   python -m venv .venv

   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   ```
2. Install dependencies:

   ```bash

   pip install -r requirements.txt

   ```
3. Configure environment variables in a `.env` file.
4. Run database migrations:

   ```bash

   python manage.py migrate

   ```
5. Start the development server:

   ```bash

   python manage.py runserver

   ```

## Notes

- Uses Wagtail CMS and Django.
- Database configuration should match your environment.
- Ignore virtual environments, logs, and `.env` in version control.
