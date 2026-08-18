from aura_skills.skills.click_element import ClickElement
from aura_skills.skills.fill_input import FillInput
from aura_skills.skills.find_login_form import FindLoginForm
from aura_skills.skills.find_search_bar import FindSearchBar
from aura_skills.skills.navigate_menu import NavigateMenu
from aura_skills.skills.select_dropdown import SelectDropdown

WEEK2_SKILLS = [
    FindLoginForm,
    FillInput,
    ClickElement,
    SelectDropdown,
    NavigateMenu,
    FindSearchBar,
]

__all__ = [
    "ClickElement",
    "FillInput",
    "FindLoginForm",
    "FindSearchBar",
    "NavigateMenu",
    "SelectDropdown",
    "WEEK2_SKILLS",
]
