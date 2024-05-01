from email_profile.where import Mode


def test_mode_all():
    assert Mode.ALL == 'ALL'


def test_mode_unseen():
    assert Mode.UNSEEN == 'UNSEEN'
