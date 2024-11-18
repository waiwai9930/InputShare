import locale
from typing import Any, TypeVar

ENGLISH_LANGUAGE = "en_"
CHINESE_LANGUAGE = "zh_"

class I18n:
    language_index: int = 0
    Candidate = TypeVar("Candidate")

    def __init__(self) -> None:
        from utils.config_manager import get_config
        user_language = get_config().language
        if user_language == ENGLISH_LANGUAGE: self.language_index = 0
        if user_language == CHINESE_LANGUAGE: self.language_index = 1

    def __call__(self, candidates: list[Candidate]) -> Any:
        if len(candidates) == 0:
            raise IndexError("Empty i18n candidates")
        if self.language_index < len(candidates):
            return candidates[self.language_index]
        return candidates[0]
    
    @staticmethod
    def language_code() -> str | None:
        code = locale.getdefaultlocale()[0]
        if code is None: return None
        if code.startswith(ENGLISH_LANGUAGE): return ENGLISH_LANGUAGE
        if code.startswith(CHINESE_LANGUAGE): return CHINESE_LANGUAGE
        return code


__i18n_instance: I18n | None = None
def get_i18n() -> I18n:
    global __i18n_instance
    if __i18n_instance is None:
        __i18n_instance = I18n()
    return __i18n_instance
