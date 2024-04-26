import os
import email

from dotenv import load_dotenv
from core import Email


def main():
    """Test"""
    load_dotenv()

    app = Email(
        server=os.getenv("EMAIL_SERVER"),
        username=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    app.login()
    data = app.backup(10)

    for item in data.email:
        print(item.number, item.subject)


if __name__ == '__main__':
    main()
