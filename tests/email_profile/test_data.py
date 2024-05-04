from json import loads
from pathlib import Path

from email_profile.data import DataClass
from email_profile.models import AttachmentModel, EmailModel

from tests.conftest import text_html   # noqa: F401


def test_instance_data():
    data = DataClass()

    assert isinstance(data, DataClass)
    assert data.email is None
    assert data.attachments == list()


def test_data_add_email():
    email = EmailModel()
    data = DataClass()
    data.add_email(model=email)

    assert isinstance(data.email, EmailModel)
    assert data.email == email


def test_data_add_attachment():
    attachment = AttachmentModel()
    data = DataClass()
    data.add_attachment(model=attachment)

    assert len(data.attachments) == 1
    assert isinstance(data.attachments[0], AttachmentModel)
    assert data.attachments[0] == attachment


def test_data_json():
    email = EmailModel(id=1)

    data = DataClass()
    data.add_email(model=email)

    response = data.json(create_file=False)

    assert isinstance(response, dict)
    assert response.get("id") == 1


def test_data_json_create_file():
    file_name = "42.json"
    path = Path("tests", "json")

    email = EmailModel(id=42)

    data = DataClass()
    data.add_email(model=email)

    data.json(
        path=path,
        create_file=True
    )

    assert path.joinpath(file_name).exists()

    with open(path.joinpath(file_name), mode="r") as file:
        email = loads(file.read())
        assert email.get("id") == 42

    path.joinpath(file_name).unlink()
    path.rmdir()


def test_data_html(text_html):  # noqa: F811
    email = EmailModel(
        id=42,
        body_text_html=text_html
    )

    data = DataClass()
    data.add_email(model=email)

    response = data.html(create_file=False)

    assert "Email Profile" in response


def test_data_html_create_file(text_html):  # noqa: F811
    file_name = "index.html"
    path = Path("tests", "html")

    email = EmailModel(
        id=42,
        body_text_html=text_html
    )

    data = DataClass()
    data.add_email(model=email)

    data.html(
        path=path,
        create_file=True
    )

    assert path.joinpath("42", file_name).exists()

    with open(path.joinpath("42", file_name), mode="r") as file:
        email = file.read()
        assert "Email Profile" in email

    path.joinpath("42", file_name).unlink()
    path.joinpath("42").rmdir()
    path.rmdir()
