from paqforms4.i18n import get_translations


def test_get_translations():
    trl_en = get_translations('en')
    trl_ru = get_translations('ru')
    assert trl_en.gettext('Invalid value') == 'Invalid value'
    assert trl_ru.gettext('Invalid value') == 'Некорректное значение'
    assert trl_en.gettext('Length <> {exact}') == 'Length <> {exact}'
    assert trl_ru.gettext('Length <> {exact}') == 'Длина <> {exact}'