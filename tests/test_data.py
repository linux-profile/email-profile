from email_profile.data import DataSqlalchemy
from email_profile.models import AttachmentModel, EmailModel


def test_instance_data_sqlalchemy():
    data = DataSqlalchemy()

    assert isinstance(data, DataSqlalchemy)
    assert data.email == None
    assert data.attachments == list()


def test_data_sqlalchemy_add_email():
    email = EmailModel()
    data = DataSqlalchemy()
    data.add_email(model=email)

    assert isinstance(data.email, EmailModel)
    assert data.email == email


def test_data_sqlalchemy_add_attachment():
    attachment = AttachmentModel()
    data = DataSqlalchemy()
    data.add_attachment(model=attachment)

    assert len(data.attachments) == 1
    assert isinstance(data.attachments[0], AttachmentModel)
    assert data.attachments[0] == attachment


def test_data_sqlalchemy_json():
    email = EmailModel(id=1)
    attachment = AttachmentModel(id=42)
    
    data = DataSqlalchemy()
    data.add_email(model=email)
    data.add_attachment(model=attachment)

    response = data.json()

    assert isinstance(response, dict)
    assert response.get("email")
    assert response.get("email")["id"] == 1
    assert response.get("attachments")[0]["id"] == 42
