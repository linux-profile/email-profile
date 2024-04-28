import os

from datetime import date
from dotenv import load_dotenv
from email_profile import Email


def main():
    """Exemple"""
    load_dotenv()

    app = Email(
        server=os.getenv("EMAIL_SERVER"),
        user=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    # Query instance
    query = app.select(mailbox="Inbox").where(subject="abc")

    # Count
    print(query.count())

    # List IDs
    ids = query.list_id()
    print(ids)

    # List Data
    data = query.list_data()

    for content in data:
        # Email data model
        print(content.email)

        # Attachments data model
        print(content.attachments)

        # Dump Json
        print(content.json())


if __name__ == '__main__':
    main()
