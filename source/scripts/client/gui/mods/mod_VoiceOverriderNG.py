# noinspection PyArgumentList,SpellCheckingInspection

from collections import namedtuple
import itertools
import random
import re

import BigWorld
import Settings
import SoundGroups
import nations
from OpenModsCore import Analytics, SimpleConfigInterface, overrideMethod
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, LOG_WARNING
from gui.battle_control import avatar_getter
from gui.game_control.special_sound_ctrl import SpecialSoundCtrl
from gui.shared.personality import ServicesLocator
from items.vehicles import VehicleDescr

from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons


VoiceMode = namedtuple('VoiceMode', ['name', 'languageMode', 'national', 'lang', 'female', 'synthetic'])
VoiceMode.__new__.__defaults__ = (None, None, False, None, False, False)
MusicMode = namedtuple('MusicMode', ['name', 'tag'])
Nation = namedtuple('Nation', ['name', 'lang', 'flag'])


NATIONS = {
    'ussr': Nation('ussr', 'RU', 'RU'),
    'germany': Nation('germany', 'DE', 'DE'),
    'usa': Nation('usa', 'EN', 'US'),
    'china': Nation('china', 'ZH_CH', 'CN'),
    'france': Nation('france', 'FR', 'FR'),
    'uk': Nation('uk', 'UK', 'UK'),
    'japan': Nation('japan', 'JA', 'JA'),
    'czech': Nation('czech', 'CS', 'CS'),
    'sweden': Nation('sweden', 'SV', 'SV'),
    'poland': Nation('poland', 'PL', 'PL'),
    'italy': Nation('italy', 'IT', 'IT'),
}
NATIONS_BY_LANG = { nation.lang: nation for nation in NATIONS.values() }


FLAGS = {
    n.flag: icons.makeImageTag(
        backport.image((R.images.gui.maps.icons.flags.c_20x12.dyn(n.name))()), width=20, height=12, vSpace=-1)
    for n in NATIONS.values()
}


I18N = {
    "name": "Ingame voice messages override",
    "UI_setting_music_text": "Ingame music mode",
    "UI_setting_music_default": "Default",
    "UI_setting_music_offspring": "The Offspring",
    "UI_setting_music_sabaton": "Sabaton",
    "UI_setting_voice_text": "Default in-game message voices",
    "UI_setting_voice_use_tank_nation_text": "Select voice matching tank's nation",
    "UI_setting_voiceAlt_text": "Alternate in-game message voices:",
    "UI_setting_voiceAlt_tooltip": "Randomly select these voices, using numeric weights",
    "UI_setting_voiceAlt_weights_text": "Relative Weights:",
    "UI_setting_voiceAlt_weights_tooltip": "Voices with the same weight have the same chance of being used",
    "UI_setting_voiceAlt_0_text": "Default message voices",
    "UI_setting_voiceAlt_0_tooltip": "Voice selected in the option menu above",
    "UI_setting_voiceAlt_0_weight_tooltip": "Press Apply before hitting the Test button if you change the weights",
    "UI_setting_button_test": "Test",
    "UI_setting_voice_nothing": "****No Override",
    "UI_setting_voice_mute": "***Mute (No voice)",
    "UI_setting_voice_random": "***Random",
    "UI_setting_voice_random_male": "***Random: male",
    "UI_setting_voice_random_female": "***Random: female ♂",
    "UI_setting_voice_default": "**Default",
    "UI_setting_voice_default_male": "**Default: male",
    "UI_setting_voice_default_female": "**Default: female",
    "UI_setting_voice_national_male": "**National: male",
    "UI_setting_voice_national_female": "**National: female",
    "UI_setting_voice_national_cs": "*National Czech: male (CS)",
    "UI_setting_voice_national_cs_female": "*National Czech: female (CS)",
    "UI_setting_voice_national_de": "*National German: male (DE)",
    "UI_setting_voice_national_de_female": "*National German: female (DE)",
    "UI_setting_voice_national_en": "*National US English: male (US)",
    "UI_setting_voice_national_en_female": "*National US English: female (US)",
    "UI_setting_voice_national_fr": "*National French: male (FR)",
    "UI_setting_voice_national_fr_female": "*National French: female (FR)",
    "UI_setting_voice_national_it": "*National Italian: male (IT)",
    "UI_setting_voice_national_it_female": "*National Italian: female (IT)",
    "UI_setting_voice_national_ja": "*National Japanese: male (JA)",
    "UI_setting_voice_national_ja_female": "*National Japanese: female (JA)",
    "UI_setting_voice_national_pl": "*National Polish: male (PL)",
    "UI_setting_voice_national_pl_female": "*National Polish: female (PL)",
    "UI_setting_voice_national_ru": "*National Russian: male (RU)",
    "UI_setting_voice_national_ru_female": "*National Russian: female (RU)",
    "UI_setting_voice_national_sv": "*National Swedish: male (SV)",
    "UI_setting_voice_national_sv_female": "*National Swedish: female (SV)",
    "UI_setting_voice_national_uk": "*National British: male (UK)",
    "UI_setting_voice_national_uk_female": "*National British: female (UK)",
    "UI_setting_voice_national_china": "*National Mandarin: male (CN)",
    "UI_setting_voice_national_china_female": "*National Mandarin: female (CN)",
    "UI_setting_voice_valkyrie_male": "Valkyria Chronicles: Welkin Gunther (JA)",
    "UI_setting_voice_valkyrie_female": "Valkyria Chronicles: Carisa Contzen (JA)",
    "UI_setting_voice_sabaton": "Celeb: Sabaton (SV)",
    "UI_setting_voice_sabaton21": "Celeb: Sabaton 2.0 (SV)",
    "UI_setting_voice_buffon": "Celeb: Gianluigi Buffon (IT)",
    "UI_setting_voice_offspring": "Celeb: The Offspring (US)",
    "UI_setting_voice_celebrity2021_ru": "Celeb: Chuck Norris (RU)",
    "UI_setting_voice_celebrity2021_en": "Celeb: Chuck Norris (US)",
    "UI_setting_voice_racer_ru": "The Great Race: Commander (RU)",
    "UI_setting_voice_racer_en": "The Great Race: Commander (US)",
    "UI_setting_voice_gup_jp_commander": "Girls und Panzer: Commander Miho (JA)",
    "UI_setting_voice_gup_jp_crew": "Girls und Panzer: Miho's Crew (JA)",
    "UI_setting_voice_duke": "G.I. Joe: Duke (US)",
    "UI_setting_voice_cobra": "G.I. Joe: Cobra",
    "UI_setting_voice_gagarin21": "Space-21: Yuri Gagarin (RU)",
    "UI_setting_voice_20_LeBwa": "CC: LeBwa (RU-20) (RU)",
    "UI_setting_voice_20_Yusha": "CC: Yusha (RU-20) (RU)",
    "UI_setting_voice_20_Amway921": "CC: Amway921 (RU-20) (RU)",
    "UI_setting_voice_20_KorbenDallas": "CC: KorbenDallas (RU-20) (RU)",
    "UI_setting_voice_20_Mailand": "CC: Mailand (EU-20) (DE)",
    "UI_setting_voice_20_Skill4ltu": "CC: Skill4ltu (EU-20) (RU)",
    "UI_setting_voice_20_Dezgamez": "CC: DezGamez (EU-20)",
    "UI_setting_voice_20_AwesomeEpicGuys": "CC: AwesomeEpicGuys (EU-20) (SV)",
    "UI_setting_voice_21_Yusha": "CC: Yusha (RU-21) (RU)",
    "UI_setting_voice_21_Vspishka": "CC: Vspishka (RU-21) (RU)",
    "UI_setting_voice_21_Amway921": "CC: Amway921 (RU-21) (RU)",
    "UI_setting_voice_21_KorbenDallas": "CC: KorbenDallas (RU-21) (RU)",
    "UI_setting_voice_21_LeBwa": "CC: LeBwa (RU-21) (RU)",
    "UI_setting_voice_21_Inspirer": "CC: Inspirer (RU-21) (RU)",
    "UI_setting_voice_21_Evil_Granny": "CC: Evil_Granny (RU-21) (RU)",
    "UI_setting_voice_21_Near_You": "CC: Near_You (RU-21) (RU)",
    "UI_setting_voice_21_Circon": "CC: Circon (EU-21) (FR)",
    "UI_setting_voice_21_Dakillzor": "CC: Dakillzor (EU-21) (FR)",
    "UI_setting_voice_21_Newmulti2k": "CC: NewMultiShow (EU-21) (PL)",
    "UI_setting_voice_21_Orzanel": "CC: Orzanel (EU-21)",
    "UI_setting_voice_21_CabMech": "CC: CabMech (NA-21) (US)",
    "UI_setting_voice_21_TragicLoss": "CC-WG: TragicLoss (NA-21) (US)",
    "UI_setting_voice_21_Cmdr_AF": "CC-WG: Cmdr_AF (NA-21) (US)",
    "UI_setting_voice_21_MasterTortoise": "CC: Kame (ASIA-21) (JA)",
    "UI_setting_voice_21_SummerTiger": "CC: Summer (ASIA-21) (KR)",
    "UI_setting_voice_21_Maharlika": "CC: Conan (ASIA-21)",
    "UI_setting_voice_armand21_en": "Waffentrager-21: Armand (FR)",
    "UI_setting_voice_armand21_ru": "Waffentrager-21: Armand (RU)",
    "UI_setting_voice_armand21_cn": "Waffentrager-21: Armand (CN)",
    "UI_setting_voice_letov21_en": "Waffentrager-21: Igor Letov (US)",
    "UI_setting_voice_letov21_ru": "Waffentrager-21: Igor Letov (RU)",
    "UI_setting_voice_letov21_cn": "Waffentrager-21: Igor Letov (CN)",
    "UI_setting_voice_elisa21_en": "Waffentrager-21: Elisa Day (US)",
    "UI_setting_voice_elisa21_ru": "Waffentrager-21: Elisa Day (RU)",
    "UI_setting_voice_elisa21_cn": "Waffentrager-21: Elisa Day (CN)",
    "UI_setting_voice_krieger21_en": "Waffentrager-21: Max von Krieger (DE)",
    "UI_setting_voice_krieger21_ru": "Waffentrager-21: Max von Krieger (RU)",
    "UI_setting_voice_krieger21_cn": "Waffentrager-21: Max von Krieger (CN)",
    "UI_setting_voice_celebrity2022_en": "Celeb: Arnold Schwarzenegger (US)",
    "UI_setting_voice_celebrity2022_ru": "Celeb: Arnold Schwarzenegger (RU)",
    "UI_setting_voice_quickyBaby": "CC: QuickyBaby (UK)",
    "UI_setting_voice_baroness22": "G.I. Joe: Baroness",
    "UI_setting_voice_coverGirl22": "G.I. Joe: Cover Girl (US)",
    "UI_setting_voice_villanelle22_en": "Waffentrager-22: Villanelle Rapière (FR)",
    "UI_setting_voice_villanelle22_ru": "Waffentrager-22: Villanelle Rapière (RU)",
    "UI_setting_voice_villanelle22_cn": "Waffentrager-22: Villanelle Rapière (CN)",
    "UI_setting_voice_ermelinda22_en": "Waffentrager-22: Ermelinda Jung (DE)",
    "UI_setting_voice_ermelinda22_ru": "Waffentrager-22: Ermelinda Jung (RU)",
    "UI_setting_voice_ermelinda22_cn": "Waffentrager-22: Ermelinda Jung (CN)",
    "UI_setting_voice_hannelore23_en": "Waffentrager-23: Hannelore Ritter (DE)",
    "UI_setting_voice_hannelore23_ru": "Waffentrager-23: Hannelore Ritter (RU)",
    "UI_setting_voice_hannelore23_cn": "Waffentrager-23: Hannelore Ritter (CN)",
    "UI_setting_voice_jana23_en": "Waffentrager-23: Jana Folta (CS)",
    "UI_setting_voice_jana23_ru": "Waffentrager-23: Jana Folta (RU)",
    "UI_setting_voice_jana23_cn": "Waffentrager-23: Jana Folta (CN)",
    "UI_setting_voice_ermelinda24_en": "Waffentrager-24: Ermelinda Jung (DE)",
    "UI_setting_voice_ermelinda24_cn": "Waffentrager-24: Ermelinda Jung (CN)",
    "UI_setting_voice_krieger24_en": "Waffentrager-24: Max von Krieger (DE)",
    "UI_setting_voice_krieger24_cn": "Waffentrager-24: Max von Krieger (CN)",
    "UI_setting_voice_mouzAkrobat24": "CC: MouzAkrobat (WT-24) (DE)",
    "UI_setting_voice_quickyBaby24": "CC: QuickyBaby (WT-24) (UK)",
    "UI_setting_voice_dakillzor24": "CC: Dakillzor (WT-24) (FR)",
    "UI_setting_voice_skill4ltu24": "CC: Skill4ltu (WT-24) (RU)",
    "UI_setting_voice_bMeng24": "Waffentrager-24: B Meng (CN)",
    "UI_setting_voice_saoNian24": "Waffentrager-24: Sao Nian (CN)",
    "UI_setting_voice_yiTuanTuan24": "Waffentrager-24: Yi Tuan Tuan (CN)",
    "UI_setting_voice_zhongPengFei24": "Waffentrager-24: Zhong Pengfei (CN)",
    "UI_setting_voice_yha_crew": "Char: Year Hare Affair (CN)",
    "UI_setting_voice_witches_commander_en": "Witches: Commander (US)",
    "UI_setting_voice_witches_commander_ru": "Witches: Commander (RU)",
    "UI_setting_voice_witches_commander_cn": "Witches: Commander (CN)",
    "UI_setting_voice_witches_crew_en": "Witches: Crew (US)",
    "UI_setting_voice_witches_crew_ru": "Witches: Crew (RU)",
    "UI_setting_voice_witches_crew_cn": "Witches: Crew (CN)",
    "UI_setting_voice_celebrity2023_en": "Celeb: Milla Jovovich (RU)",
    "UI_setting_voice_commander_bph_2022_1": "Terminator: T-800",
    "UI_setting_voice_commander_bph_2022_2": "Terminator: John Connor (US)",
    "UI_setting_voice_commander_bph_2022_3": "Terminator: Sarah Connor (US)",
    "UI_setting_voice_commander_bph_2022_4": "Terminator: T-1000",
    "UI_setting_voice_commander_bp_IvanCarevich": "Ivan Tsarevich (RU)",
    "UI_setting_voice_commander_bp_Vasilisa": "Vasilisa Beautiful (RU)",
    "UI_setting_voice_commander_bp_Kashchei": "Koschei Immortal (RU)",
    "UI_setting_voice_commander_bp_BabaYaga": "Baba Yaga (RU)",
    "UI_setting_voice_commander_mosfilm_Trus": "Mosfilm: Trus (RU)",
    "UI_setting_voice_commander_mosfilm_Balbes": "Mosfilm: Balbes (RU)",
    "UI_setting_voice_commander_mosfilm_Bivaliy": "Mosfilm: Byvaly (RU)",
    "UI_setting_voice_tankmen_bp1004_1": "Rambo: Will Teasle (US)",
    "UI_setting_voice_tankmen_bp1004_2": "Rambo: Marshall Murdock (US)",
    "UI_setting_voice_tankmen_bp1004_3": "Rambo: John Rambo (US)",
    "UI_setting_voice_tankmen_bp1004_4": "Rambo: Samuel R. Trautman (US)",
    "UI_setting_voice_tankmen_bp1004_5": "Rambo: Co Bao",
    "UI_setting_voice_handOfBlood": "CC: HandOfBlood (DE)",
    "UI_setting_voice_skill4ltu_23": "CC: Skill4ltu (WT-23) (RU)",
    "UI_setting_voice_talktomeGoose": "CC: TalkTo_MeGoose (US)",
    "UI_setting_voice_tankman_bp_12_m_5": "Dune: Gurney Halleck",
    "UI_setting_voice_tankman_bp_12_m_8": "Dune: Harkonnen Soldier (Rabban Harkonnen)",
    "UI_setting_voice_tankman_bp_12_m_9": "Dune: Sardaukar Trooper",
    "UI_setting_voice_tankman_bp_12_m_10": "Dune: Fremen Warrior (Jessica Atreides)",
    "UI_setting_voice_tankmen_bp1002_1": "Snatch: Boris The Blade Yurinov (RU)",
    "UI_setting_voice_tankmen_bp1002_3": "Snatch: Bullet-Tooth Tony (UK)",
    "UI_setting_voice_celebrity2024_en": "Celeb: Vinnie Jones (UK)",
    "UI_setting_voice_celebrity2025_en": "Celeb: Jason Statham (UK)",
    "UI_setting_voice_tankmen_bp13_1": "TMNT: Leonardo",
    "UI_setting_voice_tankmen_bp13_2": "TMNT: Donatello",
    "UI_setting_voice_tankmen_bp13_3": "TMNT: Raphael",
    "UI_setting_voice_tankmen_bp13_4": "TMNT: Michelangelo",
    "UI_setting_voice_tankmen_bp13_5": "TMNT: Shredder",
    "UI_setting_voice_tankmen_bp13_6": "TMNT: Krang",
    "UI_setting_voice_tankmen_bp13_7": "TMNT: Bebop",
    "UI_setting_voice_tankmen_bp13_8": "TMNT: Rocksteady",
    "UI_setting_voice_tankmen_bp13_9": "TMNT: April O'Neil",
    "UI_setting_voice_tankmen_bp14_5": "CC-WG: Richard 'The_Challenger' Cutland (UK)",
    "UI_setting_voice_tankmen_bp14_6": "CC-WG: David 'Eekeeboo' Baggley (UK)",
    "UI_setting_voice_tankmen_bp15_5": "Vikings: Lothbrok (SV)",
    "UI_setting_voice_tankmen_bp15_6": "Vikings: The Boneless (SV)",
    "UI_setting_voice_tankmen_bp15_7": "Vikings: Ironside (SV)",
    "UI_setting_voice_tankmen_bp15_8": "Vikings: The Shield-Maiden (SV)",
    "UI_setting_voice_tankmen_bp15_9": "Vikings: Vilgerdarson (SV)",
    "UI_setting_voice_tankmen_bp16_5": "Peaky Blinders: Tommy Shelby (UK)",
    "UI_setting_voice_tankmen_bp16_6": "Peaky Blinders: Arthur Shelby (UK)",
    "UI_setting_voice_tankmen_bp16_7": "Peaky Blinders: John Shelby (UK)",
    "UI_setting_voice_tankmen_bp16_8": "Peaky Blinders: Ada Thorne (UK)",
    "UI_setting_voice_tankmen_bp16_9": "Peaky Blinders: Michael Gray (UK)",
    "UI_setting_voice_tankmen_bp17_5": "Char: Duke Nukem (US)",
    "UI_setting_voice_tankmen_bp17_8": "Char: Lara Croft (UK)",
    "UI_setting_voice_tankmen_mtlb1_1": "CC: Guan Yu (CN)",
    "UI_setting_voice_MartyVole": "CC: Marty Vole (CS)",
    "UI_setting_voice_cygan": "CC: Cygan (PL)",
    "UI_setting_voice_kirk": "Star Trek: Kirk",
    "UI_setting_voice_spock": "Star Trek: Spock",
    "UI_setting_voice_uhura": "Star Trek: Uhura",
    "UI_setting_voice_gup_erika": "Girls und Panzer: Commander Erika (JA)",
    "UI_setting_voice_gup_mika": "Girls und Panzer: Commander Mika (JA)",
    "UI_setting_voice_gup_alice": "Girls und Panzer: Commander Alice (JA)",
    "UI_setting_voice_gup_darjeeling": "Girls und Panzer: Commander Darjeeling (JA)",
    "UI_setting_voice_gup_crew_24": "Girls und Panzer: Mika's Crew (JA)",
    "UI_setting_voice_gup_crew_25": "Girls und Panzer: 2025 Crew (JA)",
}


VOICE_MODES = [
    VoiceMode('nothing', synthetic=True),
    VoiceMode('mute', synthetic=True),
    VoiceMode('random', synthetic=True),
    VoiceMode('random_male', synthetic=True),
    VoiceMode('random_female', synthetic=True),
    VoiceMode('default', 'default'),
    VoiceMode('default_male'),
    VoiceMode('default_female', female=True),
    VoiceMode('national_male', national=True),
    VoiceMode('national_female', national=True, female=True),
    VoiceMode('national_cs', 'CS', lang='CS'),
    VoiceMode('national_cs_female', 'CS', lang='CS', female=True),
    VoiceMode('national_de', 'DE', lang='DE'),
    VoiceMode('national_de_female', 'DE', lang='DE', female=True),
    VoiceMode('national_en', 'EN', lang='EN'),
    VoiceMode('national_en_female', 'EN', lang='EN', female=True),
    VoiceMode('national_fr', 'FR', lang='FR'),
    VoiceMode('national_fr_female', 'FR', lang='FR', female=True),
    VoiceMode('national_it', 'IT', lang='IT'),
    VoiceMode('national_it_female', 'IT', lang='IT', female=True),
    VoiceMode('national_ja', 'JA', lang='JA'),
    VoiceMode('national_ja_female', 'JA', lang='JA', female=True),
    VoiceMode('national_pl', 'PL', lang='PL'),
    VoiceMode('national_pl_female', 'PL', lang='PL', female=True),
    VoiceMode('national_ru', 'RU', lang='RU'),
    VoiceMode('national_ru_female', 'RU', lang='RU', female=True),
    VoiceMode('national_sv', 'SV', lang='SV'),
    VoiceMode('national_sv_female', 'SV', lang='SV', female=True),
    VoiceMode('national_uk', 'UK', lang='UK'),
    VoiceMode('national_uk_female', 'UK', lang='UK', female=True),
    VoiceMode('national_china', 'ZH_CH', lang='CN'),
    VoiceMode('national_china_female', 'ZH_CH', lang='CN', female=True),
    VoiceMode('valkyrie_male', 'valkyrie2', lang='JA'),
    VoiceMode('valkyrie_female', 'valkyrie1', lang='JA', female=True),
    VoiceMode('sabaton', 'sabaton', lang='SV'),
    VoiceMode('buffon', 'buffon', lang='IT'),
    VoiceMode('offspring', 'offspring', lang='EN'),
    VoiceMode('celebrity2021_ru', 'celebrity2021_ru', lang='RU'),
    VoiceMode('celebrity2021_en', 'celebrity2021_en', lang='EN'),
    VoiceMode('racer_ru', 'racer_ru', lang='RU'),
    VoiceMode('racer_en', 'racer_en', lang='EN'),
    VoiceMode('20_LeBwa', 'ru1_Lebwa', lang='RU'),
    VoiceMode('20_Yusha', 'ru2_Yusha', lang='RU'),
    VoiceMode('20_Amway921', 'ru3_Amway921', lang='RU'),
    VoiceMode('20_KorbenDallas', 'ru4_KorbenDallas', lang='RU'),
    VoiceMode('20_Mailand', 'eu1_Mailand', lang='DE'),
    VoiceMode('20_Skill4ltu', 'eu2_Skill4ltu', lang='RU'),
    VoiceMode('20_Dezgamez', 'eu3_Dezgamez'),
    VoiceMode('20_AwesomeEpicGuys', 'eu4_AwesomeEpicGuys', lang='SV'),
    VoiceMode('21_Yusha', 'bb21_ru1_Yusha', lang='RU'),
    VoiceMode('21_Vspishka', 'bb21_ru1_Vspishka', lang='RU'),
    VoiceMode('21_Amway921', 'bb21_ru2_Amway921', lang='RU'),
    VoiceMode('21_KorbenDallas', 'bb21_ru2_Korbendailas', lang='RU'),
    VoiceMode('21_LeBwa', 'bb21_ru3_Lebwa', lang='RU'),
    VoiceMode('21_Inspirer', 'bb21_ru3_Inspirer', lang='RU'),
    VoiceMode('21_Evil_Granny', 'bb21_ru4_Evilgranny', lang='RU'),
    VoiceMode('21_Near_You', 'bb21_ru4_Nearyou', lang='RU'),
    VoiceMode('21_Circon', 'bb21_eu1_Circon', lang='FR'),
    VoiceMode('21_Dakillzor', 'bb21_eu2_Dakillzor', lang='FR'),
    VoiceMode('21_Newmulti2k', 'bb21_eu3_Newmulti2k', lang='PL'),
    VoiceMode('21_Orzanel', 'bb21_eu4_Orzanel'),
    VoiceMode('21_CabMech', 'bb21_na1_Cabbagemechanic', lang='EN'),
    VoiceMode('21_TragicLoss', 'bb21_na2_Tragicloss', female=True, lang='EN'),
    VoiceMode('21_Cmdr_AF', 'bb21_na3_Cmdraf', female=True, lang='EN'),
    VoiceMode('21_MasterTortoise', 'bb21_asia1_Mastertortoise', lang='JA'),
    VoiceMode('21_SummerTiger', 'bb21_asia2_Summertiger'),
    VoiceMode('21_Maharlika', 'bb21_asia3_Maharlika'),
    VoiceMode('gup_jp_commander', 'gup_jp_commander', lang='JA', female=True),
    VoiceMode('gup_jp_crew', 'gup_jp_crew', lang='JA', female=True),
    VoiceMode('duke', 'duke', lang='EN'),
    VoiceMode('cobra', 'cobra'),
    VoiceMode('gagarin21', 'gagarin21', lang='RU'),
    VoiceMode('sabaton21', 'sabaton_v2', lang='SV'),
    VoiceMode('armand21_en', 'armand21', lang='EN'),
    VoiceMode('armand21_ru', 'armand21_ru', lang='RU'),
    VoiceMode('armand21_cn', 'armand21_cn', lang='CN'),
    VoiceMode('letov21_en', 'letov21', lang='EN'),
    VoiceMode('letov21_ru', 'letov21_ru', lang='RU'),
    VoiceMode('letov21_cn', 'letov21_cn', lang='CN'),
    VoiceMode('elisa21_en', 'elisa21', lang='EN', female=True),
    VoiceMode('elisa21_ru', 'elisa21_ru', lang='RU', female=True),
    VoiceMode('elisa21_cn', 'elisa21_cn', lang='CN', female=True),
    VoiceMode('krieger21_en', 'krieger21', lang='EN'),
    VoiceMode('krieger21_ru', 'krieger21_ru', lang='RU'),
    VoiceMode('krieger21_cn', 'krieger21_cn', lang='CN'),
    VoiceMode('yha_crew', 'yha_crew', lang='CN'),
    VoiceMode('celebrity2022_en', 'celebrity2022_en', lang='EN'),
    VoiceMode('celebrity2022_ru', 'celebrity2022_ru', lang='RU'),
    VoiceMode('quickyBaby', 'quickyBaby', lang='UK'),
    VoiceMode('baroness22', 'baroness22', female=True),
    VoiceMode('coverGirl22', 'coverGirl22', female=True, lang='EN'),
    VoiceMode('villanelle22_en', 'villanelle22_en', lang='EN', female=True),
    VoiceMode('villanelle22_ru', 'villanelle22_ru', lang='RU', female=True),
    VoiceMode('villanelle22_cn', 'villanelle22_cn', lang='CN', female=True),
    VoiceMode('ermelinda22_en', 'ermelinda22_en', lang='EN', female=True),
    VoiceMode('ermelinda22_ru', 'ermelinda22_ru', lang='RU', female=True),
    VoiceMode('ermelinda22_cn', 'ermelinda22_cn', lang='CN', female=True),
    VoiceMode('witches_commander_en', 'witches_commander_en', lang='EN', female=True),
    VoiceMode('witches_commander_ru', 'witches_commander_ru', lang='RU', female=True),
    VoiceMode('witches_commander_cn', 'witches_commander_cn', lang='CN', female=True),
    VoiceMode('witches_crew_en', 'witches_crew_en', lang='EN', female=True),
    VoiceMode('witches_crew_ru', 'witches_crew_ru', lang='RU', female=True),
    VoiceMode('witches_crew_cn', 'witches_crew_cn', lang='CN', female=True),
    VoiceMode('celebrity2023_en', 'celebrity2023_en', lang='RU', female=True),
    VoiceMode('commander_bph_2022_1', 'commander_bph_2022_1'),
    VoiceMode('commander_bph_2022_2', 'commander_bph_2022_2', lang='EN'),
    VoiceMode('commander_bph_2022_3', 'commander_bph_2022_3', lang='EN', female=True),
    VoiceMode('commander_bph_2022_4', 'commander_bph_2022_4'),
    VoiceMode('commander_bp_IvanCarevich', 'commander_bp_IvanCarevich', lang='RU'),
    VoiceMode('commander_bp_Vasilisa', 'commander_bp_Vasilisa', lang='RU'),
    VoiceMode('commander_bp_Kashchei', 'commander_bp_Kashchei', lang='RU'),
    VoiceMode('commander_bp_BabaYaga', 'commander_bp_BabaYaga', lang='RU'),
    VoiceMode('commander_mosfilm_Trus', 'commander_mosfilm_Trus', lang='RU'),
    VoiceMode('commander_mosfilm_Balbes', 'commander_mosfilm_Balbes', lang='RU'),
    VoiceMode('commander_mosfilm_Bivaliy', 'commander_mosfilm_Bivaliy', lang='RU'),
    VoiceMode('handOfBlood', 'handOfBlood', lang='DE'),
    VoiceMode('hannelore23_en', 'hannelore23_en', lang='EN', female=True),
    VoiceMode('hannelore23_ru', 'hannelore23_ru', lang='RU', female=True),
    VoiceMode('hannelore23_cn', 'hannelore23_cn', lang='CN', female=True),
    VoiceMode('jana23_en', 'jana23_en', lang='EN', female=True),
    VoiceMode('jana23_ru', 'jana23_ru', lang='RU', female=True),
    VoiceMode('jana23_cn', 'jana23_cn', lang='CN', female=True),
    VoiceMode('skill4ltu_23', 'skill4ltu_23', lang='RU'),
    VoiceMode('talktomeGoose', 'talktomeGoose', lang='EN'),
    VoiceMode('tankman_bp_12_m_5', 'tankman_bp_12_m_5'),
    VoiceMode('tankman_bp_12_m_8', 'tankman_bp_12_m_8'),
    VoiceMode('tankman_bp_12_m_9', 'tankman_bp_12_m_9'),
    VoiceMode('tankman_bp_12_m_10', 'tankman_bp_12_m_10', female=True),
    VoiceMode('tankmen_bp1002_1', 'tankmen_bp1002_1', lang='RU'),
    VoiceMode('tankmen_bp1002_3', 'tankmen_bp1002_3', lang='UK'),
    VoiceMode('tankmen_bp1004_1', 'tankmen_bp1004_1', lang='EN'),
    VoiceMode('tankmen_bp1004_2', 'tankmen_bp1004_2', lang='EN'),
    VoiceMode('tankmen_bp1004_3', 'tankmen_bp1004_3', lang='EN'),
    VoiceMode('tankmen_bp1004_4', 'tankmen_bp1004_4', lang='EN'),
    VoiceMode('tankmen_bp1004_5', 'tankmen_bp1004_5', female=True),
    VoiceMode('celebrity2024_en', 'celebrity2024_en', lang='UK'),
    VoiceMode('celebrity2025_en', 'celebrity2025_en', lang='UK'),
    VoiceMode('tankmen_bp13_1', 'tankmen_bp13_1'),
    VoiceMode('tankmen_bp13_2', 'tankmen_bp13_2'),
    VoiceMode('tankmen_bp13_3', 'tankmen_bp13_3'),
    VoiceMode('tankmen_bp13_4', 'tankmen_bp13_4'),
    VoiceMode('tankmen_bp13_5', 'tankmen_bp13_5'),
    VoiceMode('tankmen_bp13_6', 'tankmen_bp13_6'),
    VoiceMode('tankmen_bp13_7', 'tankmen_bp13_7'),
    VoiceMode('tankmen_bp13_8', 'tankmen_bp13_8'),
    VoiceMode('tankmen_bp13_9', 'tankmen_bp13_9', female=True),
    VoiceMode('tankmen_bp14_5', 'tankmen_bp14_5', lang='UK'),
    VoiceMode('tankmen_bp14_6', 'tankmen_bp14_6', lang='UK'),
    VoiceMode('tankmen_bp15_5', 'tankmen_bp15_5', lang='SV'),
    VoiceMode('tankmen_bp15_6', 'tankmen_bp15_6', lang='SV'),
    VoiceMode('tankmen_bp15_7', 'tankmen_bp15_7', lang='SV'),
    VoiceMode('tankmen_bp15_8', 'tankmen_bp15_8', lang='SV', female=True),
    VoiceMode('tankmen_bp15_9', 'tankmen_bp15_9', lang='SV'),
    VoiceMode('tankmen_bp16_5', 'tankmen_bp16_5', lang='UK'),
    VoiceMode('tankmen_bp16_6', 'tankmen_bp16_6', lang='UK'),
    VoiceMode('tankmen_bp16_7', 'tankmen_bp16_7', lang='UK'),
    VoiceMode('tankmen_bp16_8', 'tankmen_bp16_8', lang='UK', female=True),
    VoiceMode('tankmen_bp16_9', 'tankmen_bp16_9', lang='UK'),
    VoiceMode('tankmen_bp17_5', 'tankmen_bp17_5', lang='EN'),
    VoiceMode('tankmen_bp17_8', 'tankmen_bp17_8', lang='UK', female=True),
    VoiceMode('tankmen_mtlb1_1', 'tankmen_mtlb1_1', lang='CN'),
    VoiceMode('MartyVole', 'MartyVole', lang='DE'),
    VoiceMode('cygan', 'cygan', lang='PL'),
    VoiceMode('kirk', 'kirk'),
    VoiceMode('spock', 'spock'),
    VoiceMode('uhura', 'uhura', female=True),
    VoiceMode('gup_erika', 'gup_erika', lang='JA', female=True),
    VoiceMode('gup_mika', 'gup_mika', lang='JA', female=True),
    VoiceMode('gup_crew_24', 'gup_crew_24', lang='JA', female=True),
    VoiceMode('gup_crew_25', 'gup_crew_25', lang='JA', female=True),
    VoiceMode('gup_alice', 'gup_alice', lang='JA', female=True),
    VoiceMode('gup_darjeeling', 'gup_darjeeling', lang='JA', female=True),
    VoiceMode('ermelinda24_en', 'ermelinda24_en', lang='EN', female=True),
    VoiceMode('ermelinda24_cn', 'ermelinda24_cn', lang='CN', female=True),
    VoiceMode('krieger24_en', 'krieger24_en', lang='EN'),
    VoiceMode('krieger24_cn', 'krieger24_cn', lang='CN'),
    VoiceMode('mouzAkrobat24', 'mouzAkrobat24', lang='DE'),
    VoiceMode('quickyBaby24', 'quickyBaby24', lang='UK'),
    VoiceMode('dakillzor24', 'dakillzor24', lang='FR'),
    VoiceMode('skill4ltu24', 'skill4ltu24', lang='RU'),
    VoiceMode('bMeng24', 'bMeng24', lang='CN'),
    VoiceMode('saoNian24', 'saoNian24', lang='CN'),
    VoiceMode('yiTuanTuan24', 'yiTuanTuan24', lang='CN'),
    VoiceMode('zhongPengFei24', 'zhongPengFei24', lang='CN'),
]
VOICE_MODES.sort(key=lambda mode: I18N.get('UI_setting_voice_%s' % mode.name, mode.name))


class ConfigInterface(SimpleConfigInterface):
    VOICE_PREVIEW = itertools.cycle(('wwsound_mode_preview01', 'wwsound_mode_preview02', 'wwsound_mode_preview03'))
    NUM_VOICE_ALTS = 20


    def __init__(self):
        self._voice_enabled = True
        self._voice_options = []
        self._previewSound = None
        self._previewNations = []

        self.voice_modes = []
        self._voice_modes_by_name = {}

        self.music_modes = [
            MusicMode('default', 'default'),
            MusicMode('offspring', 'offspringArenaMusic'),
            MusicMode('sabaton', 'sabatonArenaMusic'),
        ]
        super(ConfigInterface, self).__init__()


    def _try_voice_mode(self, mode, mode_descs):
        if mode.synthetic:
            return True
        
        if mode.languageMode is not None:
            if mode.languageMode in mode_descs:
                del mode_descs[mode.languageMode]
                return True
            if mode.languageMode in NATIONS_BY_LANG:
                return True
            LOG_WARNING('missing: ', mode)
            return False

        res = self.setSystemValue(mode_key=mode)
        LOG_NOTE('special: ', res, mode)
        return res


    def _get_mode_label(self, mode):
        label = self.i18n.get('UI_setting_voice_%s' % mode.name, mode.name).replace('*', '')

        result = re.search('\(([^)]+)\)$', label)
        if result is not None:
            lang_name = result.group(1)
            if lang_name in FLAGS:
                offset = -1 * len(result.group(0))
                label = label[:offset] + FLAGS[lang_name]
                
        if mode.female:
            label += ' <b>♂</b>'

        return label


    # Iterate over keys that try_voice_mode didn't remove:
    def _add_missing_mode_descs(self, mode_descs):
        for name in sorted(mode_descs.keys()):
            if name[:4] == 'User':
                continue
            mode_desc = mode_descs[name]
            LOG_NOTE('adding: ', mode_desc)
            self.voice_modes.append(VoiceMode(name, name))
            lang = mode_desc.voiceLanguage
            self._voice_options.append('+ ' + (lang if lang is not None and len(lang) > 0 else name))


    def _set_voice_modes(self):
        mode_descs = { name: mode_desc for name, mode_desc in SoundGroups.g_instance.soundModes.modes.items() }
        self.voice_modes = filter(lambda mode: self._try_voice_mode(mode, mode_descs), VOICE_MODES);
        self._voice_options = [ self._get_mode_label(mode) for mode in self.voice_modes ]
        self._add_missing_mode_descs(mode_descs)
        self._voice_modes_by_name = { mode.name: mode for mode in self.voice_modes }
        self._voice_modes_map = { mode.name: idx for idx, mode in enumerate(self.voice_modes) }


    def _set_default_voice_alt_conf(self):
        for i in range(0, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self.data['voiceAlt_' + num + '_sel'] = 'nothing'
            self.data['voiceAlt_' + num + '_weight'] = 0
            self.i18n['UI_setting_voiceAlt_' + num + '_sel_text'] = None
            self.i18n['UI_setting_voiceAlt_' + num + '_weight_text'] = None

        self.data['voiceAlt_0_sel'] = 'DEFAULT'


    def init(self):
        self.ID = '%(mod_ID)s'
        self.version = '2.0.0 (%(file_compile_date)s)'
        self.author = 'by Arturo Espinosa (overhaul) and Polyacov_Yury'
        self.modsGroup = 'PYmods'
        self.modSettingsID = 'PYmodsGUI'
        self.data = {'enabled': True, 'voice': 0, 'voice_name': '', 'voice_use_tank_nation': False, 'music': 0}
        self.i18n = I18N
        self._set_default_voice_alt_conf()

        super(ConfigInterface, self).init()

        self._set_voice_modes()


    def _data_voice_set_by_sel(self, sel_key, name_key):
        self.data[name_key] = self.voice_modes[self.data[sel_key]].name


    def _data_voice_set_by_name(self, sel_key, name_key):
        if name_key in self.data: 
            name = self.data[name_key]
            if name in self._voice_modes_by_name:
                self.data[sel_key] = self._voice_modes_map[name]
                return
        self._data_voice_set_by_sel(sel_key, name_key)


    def readData(self, quiet=True):
        super(ConfigInterface, self).readData()

        self._data_voice_set_by_name('voice', 'voice_name')

        for i in range(0, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self._data_voice_set_by_name('voiceAlt_' + num + '_sel',
                                         'voiceAlt_' + num + '_name')
                    
                    
    def onApplySettings(self, settings):
        self._data_voice_set_by_sel('voice', 'voice_name')

        for i in range(0, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self._data_voice_set_by_sel('voiceAlt_' + num + '_sel',
                                        'voiceAlt_' + num + '_name')

        super(ConfigInterface, self).onApplySettings(settings)


    def createTemplate(self):
        column1 = [
            self.tb.createOptions(
                'voice',
                self._voice_options,
                width=350,
                button={'iconSource': '../maps/icons/buttons/sound.png'}),
            self.tb.createControl('voice_use_tank_nation'),
            self.tb.createLabel('voiceAlt'),
            self.tb.createLabel('voiceAlt_0'),
        ]

        column2 = [
            self.tb.createOptions(
                'music', [self.i18n['UI_setting_music_%s' % mode.name] for mode in self.music_modes]),
            self.tb.createEmpty(),
            self.tb.createEmpty(),
            self.tb.createLabel('voiceAlt_weights'),
            self.tb.createSlider('voiceAlt_0_weight', 0, self.NUM_VOICE_ALTS * self.NUM_VOICE_ALTS, 1,
                                 button={
                                     'text': self.i18n['UI_setting_button_test'],
                                     'width': 75
                                 }),
        ]

        for i in range(1, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            column1.append(
                self.tb.createOptions(
                    'voiceAlt_' + num + '_sel',
                    self._voice_options,
                    width=350,
                    button={'iconSource': '../maps/icons/buttons/sound.png'})
            )
            column2.append(
                self.tb.createSlider('voiceAlt_' + num + '_weight', 0, self.NUM_VOICE_ALTS * self.NUM_VOICE_ALTS, 1)
            )

        return {
            'modDisplayName': self.i18n['name'],
            'enabled': self.data['enabled'],
            'column1': column1,
            'column2': column2
        }


    def onButtonPress(self, vName, value):
        value = int(value)
        if vName == 'voice':
            self.data['voice'] = value
            self.playPreviewSound()
        elif vName[0:9] == 'voiceAlt_' and vName[-4:] == '_sel':
            #alt_num = vName[9:vName.find('_', 9)]
            try:
                mode_key = int(value)
            except ValueError:
                mode_key = value
            self.playPreviewSound(mode_key)
        elif vName == 'voiceAlt_0_weight':
            mode = self.selectAltVoiceMode()
            self.playPreviewSound(mode)


    def onMSADestroy(self):
        self.readData()
        self.clearPreviewSound()


    def _get_voice_mode(self, mode_key=None):
        if mode_key is None:
            return self.voice_modes[self.data['voice']]
        if type(mode_key) == VoiceMode:
            return mode_key
        if type(mode_key) == int:
            return self.voice_modes[mode_key]
        if mode_key in self._voice_modes_by_name:
            return self._voice_modes_by_name[mode_key]
        return self.voice_modes[0]


    def playPreviewSound(self, mode_key=None):
        mode = self._get_voice_mode(mode_key)
        self.clearPreviewSound(mode)
        sndMgr = ServicesLocator.appLoader.getApp().soundManager
        if sndMgr is None:
            LOG_ERROR('GUI sound manager is not found')
            return
        sndPath = sndMgr.sounds.getEffectSound(next(self.VOICE_PREVIEW))
        self._previewSound = SoundGroups.g_instance.getSound2D(sndPath)
        if self._previewSound is None:
            return
        if mode.national:
            self._previewNations = list(nations.AVAILABLE_NAMES)
            self._previewSound.setCallback(lambda sound: self.playPreview(sound, mode))
            self.playPreview(self._previewSound, mode)
        else:
            self._previewSound.play()
        return True


    def clearPreviewSound(self, mode_key=None):
        if self._previewSound is not None:
            self._previewSound.stop()
            self._previewSound = None
        self.setSystemValue(mode_key=mode_key)
        vehicle = getattr(BigWorld.player(), 'vehicle', None)
        if vehicle is not None:
            vehicle.refreshNationalVoice()


    def playPreview(self, sound, mode):
        if self._previewNations and sound == self._previewSound:
            self.setSystemValue(self._previewNations.pop(), mode)
            sound.play()


    def _enableVoiceSounds(self, soundGroups, enable):
        if self._voice_enabled == enable:
            return
        self._voice_enabled = enable

        # Taken and fixed from SoundGroups.enableVoiceSounds
        # (the setVolume category says gui, should be voice)
        userPrefs = Settings.g_instance.userPrefs
        ds = userPrefs[Settings.KEY_SOUND_PREFERENCES]

        volume = 0.0 if not enable else ds.readFloat('volume_voice', 1.0)
        soundGroups.setVolume('voice', volume, False)


    def selectRandomModeWithGender(self, gender=None):
        female = None
        if gender == 'female':
            female = True
        if gender == 'male':
            female = False

        while True:
            rand = random.randint(0, len(self.voice_modes) - 1)
            mode = self.voice_modes[rand]
            if mode.synthetic:
                continue
            if female is None:
                return mode
            if mode.female == female:
                return mode


    def _selectBasicMode(self, gender=None, nation=None):
        name = 'default'
        if nation is not None:
            name = 'national'
        if gender is not None and gender != '':
            name += '_' + gender
        return self._voice_modes_by_name[name]


    def _nation_canon(self, nation):
        if nation is not None and not self.data['voice_use_tank_nation']:
            nation = None
        return nation


    def _mode_nation_elegible(self, nation, mode):
        return (nation is None or mode.national or
                (nation in NATIONS and mode.lang == NATIONS[nation].lang))


    def selectRandomMode(self, gender=None, nation=None):
        nation = self._nation_canon(nation)
            
        retries = 1000
        while retries > 0:
            retries -= 1
            mode = self.selectRandomModeWithGender(gender)
            if self._mode_nation_elegible(nation, mode):
            	return mode
        return _selectBasicMode(gender, nation)


    def _setSystemValue(self, nation=None, mode_key=None):
        mode = self._get_voice_mode(mode_key)

        soundGroups = SoundGroups.g_instance
        soundModes = soundGroups.soundModes

        if mode.synthetic:
            if mode.name == 'nothing':
                return True
            if mode.name[:6] == 'random':
                mode = self.selectRandomMode(mode.name[7:], nation)
                LOG_NOTE('random voice mode: ', mode)
            if mode.name == 'mute':
                self._enableVoiceSounds(soundGroups, False)
                return soundModes.setNationalMappingByMode('default')
            
        self._enableVoiceSounds(soundGroups, True)

        gender = SoundGroups.CREW_GENDER_SWITCHES.GENDER_ALL[mode.female]
        if mode.languageMode is not None:
            # Can't be done for all languageModes because some are actual females but are reported as male.
            if mode.languageMode in NATIONS_BY_LANG:
                soundGroups.setSwitch(SoundGroups.CREW_GENDER_SWITCHES.GROUP, gender)
            return soundModes.setMode(mode.languageMode)
        soundModes.setCurrentNation(nation or soundModes.DEFAULT_NATION, gender)
        if mode.national:
            return soundModes.setNationalMappingByPreset('NationalDefault')
        return soundModes.setNationalMappingByMode('default')


    def setSystemValue(self, nation=None, mode_key=None):
        success = self._setSystemValue(nation, mode_key)
        if not success:
            LOG_WARNING('setSystemValue mode not valid:', nation, mode_key)
        return success


    def _selectAltVoiceMode(self):
        weight_sum = sum(w for key, w in self.data.items() if key[0:9] == 'voiceAlt_' and key[-7:] == '_weight')
        if weight_sum == 0:
            return self.data['voice']
            
        rand = random.randint(0, weight_sum - 1)
        acc = 0
        for i in range(0, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            acc += self.data['voiceAlt_' + num + '_weight']
            if rand < acc:
                if i == 0:
                    break
                return self.data['voiceAlt_' + num + '_sel']
        return self.data['voice']
        

    def selectAltVoiceMode(self, nation=None):
        nation = self._nation_canon(nation)

        retries = 1000
        while retries > 0:
            retries -= 1
            mode_idx = self._selectAltVoiceMode()
            mode = self.voice_modes[mode_idx]
            if self._mode_nation_elegible(nation, mode):
            	return mode
        return self.voice_modes[self.data['voice']]


g_config = ConfigInterface()
#analytics = Analytics(g_config.ID, g_config.version, 'UA-76792179-22')


@overrideMethod(SpecialSoundCtrl, 'setPlayerVehicle')
def new_setPlayerVehicle(base, self, vehiclePublicInfo, isPlayerVehicle, *args, **kwargs):
    base(self, vehiclePublicInfo, isPlayerVehicle, *args, **kwargs)
    arena = avatar_getter.getArena()
    if not g_config.data['enabled'] or arena is None:
        return

    nation = nations.NAMES[VehicleDescr(vehiclePublicInfo.compDescr).type.id[0]]
    voice_mode = g_config.selectAltVoiceMode(nation)
    g_config.setSystemValue(nation, voice_mode)
    LOG_NOTE('voice mode: ', voice_mode)
    LOG_NOTE('vehicle nation: ', nation)
    LOG_NOTE('vehiclePublicInfo: ', vehiclePublicInfo)
    LOG_NOTE('compDescr: ', vehiclePublicInfo.compDescr)
    LOG_NOTE('VehicleDescr: ', VehicleDescr(vehiclePublicInfo.compDescr))

    self._SpecialSoundCtrl__arenaMusicSetup = musicSetup = arena.arenaType.wwmusicSetup.copy()
    tag = g_config.music_modes[g_config.data['music']].tag
    musicSetup.update(self._SpecialSoundCtrl__arenaMusicByStyle.get(tag, ()))
