from email_profile.data import DataClass
from email_profile.models import AttachmentModel, EmailModel


def test_instance_data_sqlalchemy():
    data = DataClass()

    assert isinstance(data, DataClass)
    assert data.email is None
    assert data.attachments == list()


def test_data_sqlalchemy_add_email():
    email = EmailModel()
    data = DataClass()
    data.add_email(model=email)

    assert isinstance(data.email, EmailModel)
    assert data.email == email


def test_data_sqlalchemy_add_attachment():
    attachment = AttachmentModel()
    data = DataClass()
    data.add_attachment(model=attachment)

    assert len(data.attachments) == 1
    assert isinstance(data.attachments[0], AttachmentModel)
    assert data.attachments[0] == attachment


def test_data_sqlalchemy_json():
    email = EmailModel(id=1)
    attachment = AttachmentModel(id=42)

    data = DataClass()
    data.add_email(model=email)
    data.add_attachment(model=attachment)

    response = data.json()

    assert isinstance(response, dict)
    assert response.get("email")
    assert response.get("email")["id"] == 1
    assert response.get("attachments")[0]["id"] == 42
