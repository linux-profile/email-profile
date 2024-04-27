"""
CLI Module
"""

import os

from datetime import date
from dotenv import load_dotenv
from email_profile import Email


def main():
    """Test"""
    load_dotenv()

    app = Email(
        server=os.getenv("EMAIL_SERVER"),
        user=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    # Query instance
    query = app.select(mailbox="Inbox").where(subject="abc")

    # Query result
    print(query.execute())


if __name__ == '__main__':
    main()
