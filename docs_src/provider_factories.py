"""Connect to well-known providers without remembering host names."""

from email_profile import Email


def main() -> None:
    app = Email.gmail("you@gmail.com", "app-password")
    # app = Email.outlook("you@outlook.com", "password")
    # app = Email.icloud("you@icloud.com", "app-specific-password")
    # app = Email.yahoo("you@yahoo.com", "app-password")
    # app = Email.hostinger("contato@suaempresa.com.br", "password")
    # app = Email.zoho("you@zoho.com", "password")
    # app = Email.fastmail("you@fastmail.com", "password")

    with app:
        print(f"Mailboxes: {app.mailboxes()}")


if __name__ == "__main__":
    main()
