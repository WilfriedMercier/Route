import yaml
import enum
import pathlib

class LanguageEnum(enum.Enum):
    r'''Allowed languages in the application.'''

    ENGLISH = 'en'
    FRENCH  = 'fr'

class LanguageHandler:

    def __init__(self, translations: dict, default_language: LanguageEnum = LanguageEnum.ENGLISH):

        self.translations = translations
        self.language     = default_language

    @property
    def languages(self) -> list[LanguageEnum]: 
        return [lang for lang in self.translations.keys()]

    @property
    def language(self) -> LanguageEnum: return self._language
    
    @language.setter
    def language(self, lang: LanguageEnum) -> None:

        self._language   = lang
        self.translation = self.translations[self.language]
    
        return
    
    @property
    def dropdown_text_language(self) -> str:
        return self.map_language_to_dropdown_text(self.language)
    
    @staticmethod
    def map_language_to_dropdown_text(lang: LanguageEnum) -> str:

        return {
            LanguageEnum.ENGLISH : 'En 🇬🇧',
            LanguageEnum.FRENCH  : 'Fr 🇫🇷'
        }[lang]
    
    @staticmethod
    def map_dropdown_text_to_language(lang: str) -> LanguageEnum:

        return {
            'En 🇬🇧' : LanguageEnum.ENGLISH,
            'Fr 🇫🇷' : LanguageEnum.FRENCH
        }[lang]
    
    def __getitem__(self, key):
        """Enables instance[key] syntax. Delegates the access to self.translation."""

        return self.translation[key]

def map_string_code_to_language(lang: str) -> LanguageEnum:
    r'''
    Maps a string representing a language to its Enum representation.

    :param lang: language string to transform into an enum
    '''

    if   lang.lower() == 'en' : return LanguageEnum.ENGLISH
    elif lang.lower() == 'fr' : return LanguageEnum.FRENCH
    else: raise ValueError(f'Language {lang} not supported.')

def load_language(lang: LanguageEnum) -> dict:
    r"""
    Load the language file for the given language code.

    :param lang: language to load the translation
    """

    file = pathlib.Path('lang') / f'{lang.value}.yaml'

    if not file.exists(): raise ValueError(f'Language file for code "{lang}" does not exist.')

    with open(file, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
    
def load_languages(langs: list[LanguageEnum]) -> dict[str, dict]:
    r"""
    Load multiple language files for the given list of language codes.

    :param lang: list of languages to load the translation
    """

    languages = {}

    for lang in langs:
        languages[lang] = load_language(lang)

    return languages