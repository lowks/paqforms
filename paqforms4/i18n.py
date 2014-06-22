# TODO see locale tuples in WTForms
import os.path as op; __dir__ = op.dirname(__file__)
import babel.support


translations_cache = {}
localedir = op.join(__dir__, 'translations')


# HELPERS
def get_translations(locale):
    if str(locale) not in translations_cache:
        translations_cache[str(locale)] = babel.support.Translations.load(localedir, locales=[locale])
    return translations_cache[str(locale)]