import yaml
import enum
import pathlib
from   typing import Literal, get_args

# Allowed languages for the UI
LANGUAGE = Literal['en', 'fr']

class LanguageHandler:
    r'''
    Object handling the language update of the application.

    :param translations: a dictionary of translations in different languages
    '''

    def __init__(self, translations: dict[LANGUAGE, dict]): self._translations = translations

    @property
    def translations(self): return self._translations

    @property
    def languages(self) -> list[LANGUAGE]: return [lang for lang in self.translations.keys()]
    
    def map_language_to_dropdown_text(self, lang: LANGUAGE) -> str:
        r'''
        Return the language select ion dropdown associated to each language.

        :param lang: language to get the dropdown text for
        '''

        return {'en' : 'En 🇬🇧', 'fr' : 'Fr 🇫🇷'}[lang]
    
    def map_dropdown_text_to_language(self, text: str) -> LANGUAGE:

        return {'En 🇬🇧' : 'en', 'Fr 🇫🇷' : 'fr'}[text]  # type: ignore

    def __getitem__(self, key): return self.translations[key]
    
def is_language_correct(lang: str) -> bool: return lang.lower() in get_args(LANGUAGE)

def are_languages_correct(languages: list[str]) -> list[LANGUAGE]:

    if any(not is_language_correct(lang) for lang in languages): 
        raise IOError('At least one of the language files is not recognised.')
    
    return languages # type: ignore

def load_language(lang: LANGUAGE) -> dict:
    r"""
    Load the language file for the given language code.

    :param lang: language to load the translation
    """

    file = pathlib.Path('lang') / f'{lang}.yaml'

    if not file.exists(): raise ValueError(f'Language file for code "{lang}" does not exist.')

    with open(file, 'r') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
    
def load_languages(langs: list[LANGUAGE]) -> dict[LANGUAGE, dict]:
    r"""
    Load multiple language files for the given list of language codes.

    :param lang: list of languages to load the translation
    """

    languages = {}

    for lang in langs: languages[lang] = load_language(lang)

    return languages