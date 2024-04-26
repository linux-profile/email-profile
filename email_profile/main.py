import os
import email

from dotenv import load_dotenv
from core import _Email


def main():
    """Test"""
    load_dotenv()

    app = _Email(
        server=os.getenv("EMAIL_SERVER"),
        user=os.getenv("EMAIL_USERNAME"),
        password=os.getenv("EMAIL_PASSWORD")
    )

    total = app.select(exception=False).count().execute()
    print(total)

    # app.login()
    # data = app.backup(10)

    # for item in data.email:
    #     print(item.number, item.subject)


if __name__ == '__main__':
    main()
