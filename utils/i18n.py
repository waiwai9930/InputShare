import locale
from typing import TypeVar

def i18n_factory():
    user_language = locale.getdefaultlocale()[0]
    language_index = 0
    T = TypeVar('T')
    if user_language in ["zh", "zh_CN", "zh_HK", "zh_MO", "zh_SG", "zh_TW"]:
        language_index = 1

    def i18n_instance(candidates: list[T]) -> T:
        if len(candidates) == 0:
            raise Exception("Empty i18n candidates")
        if language_index < len(candidates):
            return candidates[language_index]
        return candidates[0]
    return i18n_instance

I18N = i18n_factory()
