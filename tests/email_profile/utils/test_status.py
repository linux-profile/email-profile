from email_profile.utils import Status, StatusResponse


def test_status_ok():
    assert Status.OK == 'OK'


def test_status_no():
    assert Status.NO == 'NO'


def test_status_bad():
    assert Status.BAD == 'BAD'


def test_status_status_response():
    assert_type = True
    assert_message = "Ok!"

    status_response = StatusResponse(
        type=assert_type,
        message=assert_message
    )

    assert status_response.type is assert_type
    assert status_response.message == assert_message


def test_status_instance_validate_status():
    input_status = 'OK'
    validate = Status.validate_status(input_status)

    assert isinstance(validate, StatusResponse)


def test_status_validate_status_ok():
    input_status = 'OK'
    validate = Status.validate_status(input_status)

    assert validate.type is True
    assert validate.message == "Login completed, now in authenticated state"


def test_status_validate_status_no():
    input_status = 'NO'
    validate = Status.validate_status(
        status=input_status,
        raise_error=False
    )

    assert validate.type is False
    assert validate.message == "Login failure: user name or password rejected"


def test_status_validate_status_bad():
    input_status = 'BAD'
    validate = Status.validate_status(
        status=input_status,
        raise_error=False
    )

    assert validate.type is False
    assert validate.message == "Command unknown or arguments invalid"


def test_status_validate_data_with_data():
    input_status = [b'4 8 15 16 23 42']
    output_status = ['4', '8', '15', '16', '23', '42']

    assert Status.validate_data(input_status) == output_status


def test_status_validate_data_no_data():
    input_status = [b'']
    output_status = []

    assert Status.validate_data(input_status) == output_status


def test_status_validate_status_with_error_no():
    input_status = 'NO'
    try:
        Status.validate_status(
            status=input_status,
            raise_error=True
        )
    except Exception as error:
        current_error = error.args[0]

    assert current_error == "Login failure: user name or password rejected"


def test_status_validate_status_with_error_bad():
    input_status = 'BAD'
    try:
        Status.validate_status(
            status=input_status,
            raise_error=True
        )
    except Exception as error:
        current_error = error.args[0]

    assert current_error == "Command unknown or arguments invalid"


def test_status_validate_status_with_error_unknown():
    input_status = ''
    try:
        Status.validate_status(
            status=input_status,
            raise_error=True
        )
    except Exception as error:
        current_error = error.args[0]

    assert current_error == "Unknown error"


def test_status_validate_status_no_error():
    input_status = ''

    validate = Status.validate_status(
        status=input_status,
        raise_error=False
    )

    assert validate.type is False
    assert validate.message == "Unknown error"
