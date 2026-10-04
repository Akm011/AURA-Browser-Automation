from aura_skills.skills.click_element import ClickElement
from aura_skills.skills.download_file import DownloadFile
from aura_skills.skills.extract_text import ExtractText
from aura_skills.skills.fill_input import FillInput
from aura_skills.skills.find_login_form import FindLoginForm
from aura_skills.skills.find_search_bar import FindSearchBar
from aura_skills.skills.navigate_menu import NavigateMenu
from aura_skills.skills.press_key import PressKey
from aura_skills.skills.scroll_page import ScrollPage
from aura_skills.skills.select_dropdown import SelectDropdown
from aura_skills.skills.upload_file import UploadFile
from aura_skills.skills.wait import Wait

WEEK2_SKILLS = [
    FindLoginForm,
    FillInput,
    ClickElement,
    SelectDropdown,
    NavigateMenu,
    FindSearchBar,
    Wait,
    PressKey,
    ScrollPage,
    ExtractText,
    DownloadFile,
    UploadFile,
]

__all__ = [
    "ClickElement",
    "DownloadFile",
    "ExtractText",
    "FillInput",
    "FindLoginForm",
    "FindSearchBar",
    "NavigateMenu",
    "PressKey",
    "ScrollPage",
    "SelectDropdown",
    "UploadFile",
    "Wait",
    "WEEK2_SKILLS",
]
