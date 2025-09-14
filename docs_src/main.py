"""Email Profile"""

import os

from datetime import date

from dotenv import load_dotenv

from _email_profile.email import Email


def main():
    load_dotenv()

    email = Email(
        server=os.getenv("SERVER"),
        user=os.getenv("EMAIL"),
        password=os.getenv("PASSWORD"),
    )
    email.load(params={"since": date.today()})
    # email.select.inbox_applications_twitch.where(
    #     params={"since": date.today()}
    # )


if __name__ == "__main__":
    main()
