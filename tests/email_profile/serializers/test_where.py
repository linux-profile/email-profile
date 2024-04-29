from datetime import datetime, date
from email_profile.serializers import WhereSerializer


def test_instance_where_serializer():
    data = WhereSerializer()

    assert isinstance(data, WhereSerializer)
    assert data.since == ''
    assert data.before == ''
    assert data.subject == ''
    assert data.from_who == ''


def test_where_serializer_since():
    test_date = datetime(1996, 5, 31)
    assert_date = test_date.strftime('%d-%b-%Y')

    serializer = WhereSerializer(since=test_date)
    assert serializer.since == f'(SINCE {assert_date})'


def test_where_serializer_since_wrong_data_type():
    test_date = "1996-5-31"
    test_assert = "Attribute validation error (SINCE)."

    try:
        WhereSerializer(since=test_date)
    except AttributeError as error:
        current_error = error.args[0]

    assert current_error == test_assert


def test_where_serializer_before():
    test_date = date.today()
    assert_date = test_date.strftime('%d-%b-%Y')

    serializer = WhereSerializer(before=test_date)
    assert serializer.before == f'(BEFORE {assert_date})'


def test_where_serializer_before_wrong_data_type():
    test_date = "1996-5-31"
    test_assert = "Attribute validation error (BEFORE)."

    try:
        WhereSerializer(before=test_date)
    except AttributeError as error:
        current_error = error.args[0]

    assert current_error == test_assert


def test_where_serializer_subject_no_special_characters():
    test_string = "Important email"
    assert_string = "Important email"

    serializer = WhereSerializer(subject=test_string)
    assert serializer.subject == f'(SUBJECT "{assert_string}")'


def test_where_serializer_subject_with_special_characters():
    test_string = "Important êmail"
    assert_string = "Important mail"

    serializer = WhereSerializer(subject=test_string)
    assert serializer.subject == f'(SUBJECT "{assert_string}")'


def test_where_serializer_from_who_no_special_characters():
    test_string = "email@test.com"
    assert_string = "email@test.com"

    serializer = WhereSerializer(from_who=test_string)
    assert serializer.from_who == f'(FROM "{assert_string}")'


def test_where_serializer_from_who_with_special_characters():
    test_string = "êmail@test.com"
    assert_string = "mail@test.com"

    serializer = WhereSerializer(from_who=test_string)
    assert serializer.from_who == f'(FROM "{assert_string}")'


def test_where_serializer_result():
    input_since = datetime(1996, 5, 31)
    input_before = date.today()
    input_subject = 'abc'

    output_since = input_since.strftime('%d-%b-%Y')
    output_before = input_before.strftime('%d-%b-%Y')
    output_subject = input_subject
    output_result = f'(SINCE {output_since}) (BEFORE {output_before}) (SUBJECT "{output_subject}")'

    serializer = WhereSerializer(
        since=input_since,
        before=input_before,
        subject=input_subject
    )

    assert serializer.result() == output_result
