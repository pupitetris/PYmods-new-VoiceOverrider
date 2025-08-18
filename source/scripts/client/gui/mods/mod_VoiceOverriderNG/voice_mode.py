from collections import namedtuple
import re

from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import icons
import nations

from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, LOG_WARNING


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
NATIONS_AVAILABLE_NAMES = nations.AVAILABLE_NAMES


FLAGS = {
    n.flag: icons.makeImageTag(
        backport.image((R.images.gui.maps.icons.flags.c_20x12.dyn(n.name))()), width=20, height=12, vSpace=-1)
    for n in NATIONS.values()
}


def _cast(value, _type):
    if type(value) != _type:
        raise TypeError('value ' + repr(value) + ' expected as ' + str(_type) + ' but is ' + str(type(value)))
    return _type(value)


def _castOrNone(value, _type):
    if value is None:
        return None
    return _cast(value, _type)


class VoiceMode(object):
    def __init__(self, name, languageMode=None, national=False, lang=None, female=False,
                 synthetic=False, icon=None, label=None, short_label=None, enabled=True, idx=None):

        self.idx = _castOrNone(idx, int)
        self.name = _cast(name, str)
        self.languageMode = _castOrNone(languageMode, str)
        self.national = _cast(national, bool)

        self.lang = lang
        if lang is not None and lang not in NATIONS_BY_LANG:
            raise ValueError('lang ' + str(lang) + ' not valid')

        self.female = _cast(female, bool)
        self.synthetic = _cast(synthetic, bool)

        self.icon = icon
        if icon is not None and type(icon) != str and type(icon) != list:
            raise TypeError('icon ' + str(icon) + ' expected as str, list or None but is ' + str(type(icon)))

        self.label = _castOrNone(label, str)
        self.short_label = _castOrNone(short_label, str)
        self.enabled = _cast(enabled, bool)

        self._i18n = None
        self._i18n_short = None


    def __repr__(self):
        return 'VoiceMode(' + \
            'idx=' + repr(self.idx) + \
            ', name=' + repr(self.name) + \
            ', languageMode=' + repr(self.languageMode) + \
            ', national=' + repr(self.national) + \
            ', lang=' + repr(self.lang) + \
            ', female=' + repr(self.female) + \
            ', synthetic=' + repr(self.synthetic) + \
            ', icon=' + repr(self.icon) + \
            ', label=' + repr(self.label) + \
            ', short_label=' + repr(self.label) + \
            ', enabled=' + repr(self.enabled) + \
            ')'


    def is_available(self, mode_descs=None):
        if self.synthetic:
            return self.enabled
        if self.languageMode is not None:
            if mode_descs is not None and self.languageMode in mode_descs:
                del mode_descs[self.languageMode]
                return self.enabled
            if self.languageMode in NATIONS_BY_LANG:
                return self.enabled
            LOG_WARNING('missing: ', self)
            return False

        return None


    def _get_i18n_label(self, i18n, short):
        i18n_prefix = 'voice_short_%s' if short else 'UI_setting_voice_%s'
        return i18n.get(i18n_prefix % self.name, self.name).replace('*', '')


    def _get_label_with_gender(self, i18n, short):
        return self.get_label(i18n, short, False) + (' <b>♂</b>' if self.female else '')


    def get_label(self, i18n=None, short=False, with_gender=False):
        if with_gender:
            return self._get_label_with_gender(i18n, short)
        if not short and self.label is not None:
            return self.label
        if short and self.short_label is not None:
            return self.short_label

        if self._i18n is None:
            if i18n is None:
                LOG_WARNING('mode get_label but label not set', self)
                return self.name
            self._i18n = self._get_i18n_label(i18n, False)
            self._i18n_short = self._get_i18n_label(i18n, True)

        label = self._i18n_short if short else self._i18n

        result = re.search('\(([^)]+)\)$', label)
        if result is not None:
            lang_name = result.group(1)
            if lang_name in FLAGS:
                offset = -1 * len(result.group(0))
                label = label[:offset] + FLAGS[lang_name]

        if short:
            self.short_label = label
        else:
            self.label = label

        return label


VOICE_MODES = [
    VoiceMode('nothing', synthetic=True),
    VoiceMode('mute', synthetic=True),
    VoiceMode('random', synthetic=True, icon='crewSkins/FoolsDay_Rngesus'),
    VoiceMode('random_male', synthetic=True, icon='crewSkins/FoolsDay_Rngesus'),
    VoiceMode('random_female', synthetic=True, icon='crewSkins/FoolsDay_Rngesus'),
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
    VoiceMode('national_china', 'ZH_CH', lang='ZH_CH'),
    VoiceMode('national_china_female', 'ZH_CH', lang='ZH_CH', female=True),
    VoiceMode('valkyrie_male', 'valkyrie2', lang='JA', icon='japan_Welkin_Gunther'),
    VoiceMode('valkyrie_female', 'valkyrie1', lang='JA', female=True, icon='japan_Carisa_Contzen'),
    VoiceMode('sabaton', 'sabaton', lang='SV', icon='sweden_34'),
    VoiceMode('buffon', 'buffon', lang='IT', icon='italy_Buffon'),
    VoiceMode('offspring', 'offspring', lang='EN', icon='usa_44'),
    VoiceMode('celebrity2021_ru', 'celebrity2021_ru', lang='RU', icon='ny21_men'),
    VoiceMode('celebrity2021_en', 'celebrity2021_en', lang='EN', icon='ny21_men'),
    VoiceMode('racer_ru', 'racer_ru', lang='RU', icon='race19_commander_b'),
    VoiceMode('racer_en', 'racer_en', lang='EN', icon='race19_commander_a'),
    VoiceMode('20_LeBwa', 'ru1_Lebwa', lang='RU', icon='bob20_commander1_ru'),
    VoiceMode('20_Yusha', 'ru2_Yusha', lang='RU', icon='bob20_commander2_ru'),
    VoiceMode('20_Amway921', 'ru3_Amway921', lang='RU', icon='bob20_commander3_ru'),
    VoiceMode('20_KorbenDallas', 'ru4_KorbenDallas', lang='RU', icon='bob20_commander4_ru'),
    VoiceMode('20_Mailand', 'eu1_Mailand', lang='DE', icon='bob20_commander1_eu'),
    VoiceMode('20_Skill4ltu', 'eu2_Skill4ltu', lang='RU', icon='bob20_commander2_eu'),
    VoiceMode('20_Dezgamez', 'eu3_Dezgamez', icon='bob20_commander3_eu'),
    VoiceMode('20_AwesomeEpicGuys', 'eu4_AwesomeEpicGuys', lang='SV', icon='bob20_commander4_eu'),
    VoiceMode('21_Yusha', 'bb21_ru1_Yusha', lang='RU', icon='bob21_blogger8_ru'),
    VoiceMode('21_Vspishka', 'bb21_ru1_Vspishka', lang='RU', icon='bob21_blogger7_ru'),
    VoiceMode('21_Amway921', 'bb21_ru2_Amway921', lang='RU', icon='bob21_blogger1_ru'),
    VoiceMode('21_KorbenDallas', 'bb21_ru2_Korbendailas', lang='RU', icon='bob21_blogger4_ru'),
    VoiceMode('21_LeBwa', 'bb21_ru3_Lebwa', lang='RU', icon='bob21_blogger5_ru'),
    VoiceMode('21_Inspirer', 'bb21_ru3_Inspirer', lang='RU', icon='bob21_blogger3_ru'),
    VoiceMode('21_Evil_Granny', 'bb21_ru4_Evilgranny', lang='RU', icon='bob21_blogger2_ru'),
    VoiceMode('21_Near_You', 'bb21_ru4_Nearyou', lang='RU', icon='bob21_blogger6_ru'),
    VoiceMode('21_Circon', 'bb21_eu1_Circon', lang='FR', icon='bob21_blogger1_eu'),
    VoiceMode('21_Dakillzor', 'bb21_eu2_Dakillzor', lang='FR', icon='bob21_blogger2_eu'),
    VoiceMode('21_Newmulti2k', 'bb21_eu3_Newmulti2k', lang='PL', icon='bob21_blogger3_eu'),
    VoiceMode('21_Orzanel', 'bb21_eu4_Orzanel', icon='bob21_blogger4_eu'),
    VoiceMode('21_CabMech', 'bb21_na1_Cabbagemechanic', lang='EN', icon='bob21_blogger1_na'),
    VoiceMode('21_TragicLoss', 'bb21_na2_Tragicloss', female=True, lang='EN', icon='bob21_blogger3_na'),
    VoiceMode('21_Cmdr_AF', 'bb21_na3_Cmdraf', female=True, lang='EN', icon='bob21_blogger2_na'),
    VoiceMode('21_MasterTortoise', 'bb21_asia1_Mastertortoise', lang='JA', icon='bob21_blogger2_asia'),
    VoiceMode('21_SummerTiger', 'bb21_asia2_Summertiger', icon='bob21_blogger3_asia'),
    VoiceMode('21_Maharlika', 'bb21_asia3_Maharlika', icon='bob21_blogger1_asia'),
    VoiceMode('gup_jp_commander', 'gup_jp_commander', lang='DE', female=True, icon='girls_und_panzer_nishizumi'),
    VoiceMode('gup_jp_crew', 'gup_jp_crew', lang='DE', female=True, icon=['girls_und_panzer_takebe', 'girls_und_panzer_isuzu', 'girls_und_panzer_akiyama', 'girls_und_panzer_reizei']),
    VoiceMode('duke', 'duke', lang='EN', icon='twitch14'),
    VoiceMode('cobra', 'cobra', icon='twitch15'),
    VoiceMode('gagarin21', 'gagarin21', lang='RU', icon='gagarin21'),
    VoiceMode('sabaton21', 'sabaton_v2', lang='SV', icon='sweden_38'),
    VoiceMode('armand21_en', 'armand21', lang='FR', icon='hunter_3'),
    VoiceMode('armand21_ru', 'armand21_ru', lang='RU', icon='hunter_3'),
    VoiceMode('armand21_cn', 'armand21_cn', lang='ZH_CH', icon='hunter_3'),
    VoiceMode('letov21_en', 'letov21', lang='EN', icon='hunter_1'),
    VoiceMode('letov21_ru', 'letov21_ru', lang='RU', icon='hunter_1'),
    VoiceMode('letov21_cn', 'letov21_cn', lang='ZH_CH', icon='hunter_1'),
    VoiceMode('elisa21_en', 'elisa21', lang='EN', female=True, icon='hunter_2'),
    VoiceMode('elisa21_ru', 'elisa21_ru', lang='RU', female=True, icon='hunter_2'),
    VoiceMode('elisa21_cn', 'elisa21_cn', lang='ZH_CH', female=True, icon='hunter_2'),
    VoiceMode('krieger21_en', 'krieger21', lang='DE', icon='boss'),
    VoiceMode('krieger21_ru', 'krieger21_ru', lang='RU', icon='boss'),
    VoiceMode('krieger21_cn', 'krieger21_cn', lang='ZH_CH', icon='boss'),
    VoiceMode('yha_crew', 'yha_crew', lang='ZH_CH', icon=['YHA_commander', 'YHA_driver', 'YHA_gunner', 'YHA_loader', 'YHA_radio']),
    VoiceMode('celebrity2022_en', 'celebrity2022_en', lang='EN', icon='ny22_men'),
    VoiceMode('celebrity2022_ru', 'celebrity2022_ru', lang='RU', icon='ny22_men'),
    VoiceMode('quickyBaby', 'quickyBaby', lang='UK', icon='commander_quickybaby'),
    VoiceMode('baroness22', 'baroness22', female=True, icon='gi_joe_2022_baroness'),
    VoiceMode('coverGirl22', 'coverGirl22', female=True, lang='EN', icon='gi_joe_2022_cover_girl'),
    VoiceMode('villanelle22_en', 'villanelle22_en', lang='EN', female=True, icon='wt_2022_hunter'),
    VoiceMode('villanelle22_ru', 'villanelle22_ru', lang='RU', female=True, icon='wt_2022_hunter'),
    VoiceMode('villanelle22_cn', 'villanelle22_cn', lang='ZH_CH', female=True, icon='wt_2022_hunter'),
    VoiceMode('ermelinda22_en', 'ermelinda22_en', lang='EN', female=True, icon='wt_2022_boss'),
    VoiceMode('ermelinda22_ru', 'ermelinda22_ru', lang='RU', female=True, icon='wt_2022_boss'),
    VoiceMode('ermelinda22_cn', 'ermelinda22_cn', lang='ZH_CH', female=True, icon='wt_2022_boss'),
    VoiceMode('witches_commander_en', 'witches_commander_en', lang='EN', female=True, icon='hw22_witch_kordelia'),
    VoiceMode('witches_commander_ru', 'witches_commander_ru', lang='RU', female=True, icon='hw22_witch_kordelia'),
    VoiceMode('witches_commander_cn', 'witches_commander_cn', lang='ZH_CH', female=True, icon='hw22_witch_kordelia'),
    VoiceMode('witches_crew_en', 'witches_crew_en', lang='EN', female=True, icon=['hw22_witch_aurelia', 'hw22_witch_deirdra', 'hw22_witch_sibilla']),
    VoiceMode('witches_crew_ru', 'witches_crew_ru', lang='RU', female=True, icon=['hw22_witch_aurelia', 'hw22_witch_deirdra', 'hw22_witch_sibilla']),
    VoiceMode('witches_crew_cn', 'witches_crew_cn', lang='ZH_CH', female=True, icon=['hw22_witch_aurelia', 'hw22_witch_deirdra', 'hw22_witch_sibilla']),
    VoiceMode('celebrity2023_en', 'celebrity2023_en', lang='RU', female=True, icon='ny23_girl_m'),
    VoiceMode('commander_bph_2022_1', 'commander_bph_2022_1', icon='bp_commander_h_1'),
    VoiceMode('commander_bph_2022_2', 'commander_bph_2022_2', lang='EN', icon='bp_commander_h_2'),
    VoiceMode('commander_bph_2022_3', 'commander_bph_2022_3', lang='EN', female=True, icon='bp_commander_h_3'),
    VoiceMode('commander_bph_2022_4', 'commander_bph_2022_4', icon='bp_commander_h_4'),
    VoiceMode('commander_bp_IvanCarevich', 'commander_bp_IvanCarevich', lang='RU'),
    VoiceMode('commander_bp_Vasilisa', 'commander_bp_Vasilisa', lang='RU'),
    VoiceMode('commander_bp_Kashchei', 'commander_bp_Kashchei', lang='RU'),
    VoiceMode('commander_bp_BabaYaga', 'commander_bp_BabaYaga', lang='RU'),
    VoiceMode('commander_mosfilm_Trus', 'commander_mosfilm_Trus', lang='RU'),
    VoiceMode('commander_mosfilm_Balbes', 'commander_mosfilm_Balbes', lang='RU'),
    VoiceMode('commander_mosfilm_Bivaliy', 'commander_mosfilm_Bivaliy', lang='RU'),
    VoiceMode('handOfBlood', 'handOfBlood', lang='DE', icon='HandOfBlood', enabled=False),
    VoiceMode('hannelore23_en', 'hannelore23_en', lang='EN', female=True, icon='wt_2023_hannelore'),
    VoiceMode('hannelore23_ru', 'hannelore23_ru', lang='RU', female=True, icon='wt_2023_hannelore'),
    VoiceMode('hannelore23_cn', 'hannelore23_cn', lang='ZH_CH', female=True, icon='wt_2023_hannelore'),
    VoiceMode('jana23_en', 'jana23_en', lang='EN', female=True, icon='wt_2023_driver'),
    VoiceMode('jana23_ru', 'jana23_ru', lang='RU', female=True, icon='wt_2023_driver'),
    VoiceMode('jana23_cn', 'jana23_cn', lang='ZH_CH', female=True, icon='wt_2023_driver'),
    VoiceMode('talktomeGoose', 'talktomeGoose', lang='EN', icon='tc2023_commander_1'),
    VoiceMode('skill4ltu_23', 'skill4ltu_23', lang='RU', icon='tc2023_commander_2'),
    VoiceMode('tankman_bp_12_m_5', 'tankman_bp_12_m_5', female=True, icon='tankmen_bp12_5'),
    VoiceMode('tankman_bp_12_m_8', 'tankman_bp_12_m_8', icon=['tankmen_bp12_8', 'tankmen_bp12_7']),
    VoiceMode('tankman_bp_12_m_9', 'tankman_bp_12_m_9', icon=['tankmen_bp12_9', 'tankmen_bp12_6']),
    VoiceMode('tankman_bp_12_m_10', 'tankman_bp_12_m_10', enabled=False),
    VoiceMode('tankmen_bp1002_1', 'tankmen_bp1002_1', lang='RU', icon='tankmen_bp1002_1'),
    VoiceMode('tankmen_bp1002_3', 'tankmen_bp1002_3', lang='UK', icon='tankmen_bp1002_3'),
    VoiceMode('tankmen_bp1004_1', 'tankmen_bp1004_1', lang='EN', icon='tankmen_bp1004_1'),
    VoiceMode('tankmen_bp1004_2', 'tankmen_bp1004_2', lang='EN', icon='tankmen_bp1004_2'),
    VoiceMode('tankmen_bp1004_3', 'tankmen_bp1004_3', lang='EN', icon='tankmen_bp1004_3'),
    VoiceMode('tankmen_bp1004_4', 'tankmen_bp1004_4', lang='EN', icon='tankmen_bp1004_4'),
    VoiceMode('tankmen_bp1004_5', 'tankmen_bp1004_5', female=True, icon='tankmen_bp1004_5'),
    VoiceMode('celebrity2024_en', 'celebrity2024_en', lang='UK', icon='ny24_men'),
    VoiceMode('celebrity2025_en', 'celebrity2025_en', lang='UK', icon='ny25_men'),
    VoiceMode('tankmen_bp13_1', 'tankmen_bp13_1', icon='tankmen_bp13_1'),
    VoiceMode('tankmen_bp13_2', 'tankmen_bp13_2', icon='tankmen_bp13_2'),
    VoiceMode('tankmen_bp13_3', 'tankmen_bp13_3', icon='tankmen_bp13_3'),
    VoiceMode('tankmen_bp13_4', 'tankmen_bp13_4', icon='tankmen_bp13_4'),
    VoiceMode('tankmen_bp13_5', 'tankmen_bp13_5', icon='tankmen_bp13_5'),
    VoiceMode('tankmen_bp13_6', 'tankmen_bp13_6', icon='tankmen_bp13_6'),
    VoiceMode('tankmen_bp13_7', 'tankmen_bp13_7', icon='tankmen_bp13_7'),
    VoiceMode('tankmen_bp13_8', 'tankmen_bp13_8', icon='tankmen_bp13_8'),
    VoiceMode('tankmen_bp13_9', 'tankmen_bp13_9', female=True, icon='tankmen_bp13_9'),
    VoiceMode('tankmen_bp14_5', 'tankmen_bp14_5', lang='UK', icon='bp_commander_14_5'),
    VoiceMode('tankmen_bp14_6', 'tankmen_bp14_6', lang='UK', icon='bp_commander_14_6'),
    VoiceMode('tankmen_bp15_5', 'tankmen_bp15_5', lang='SV', icon='tankmen_bp15_5'),
    VoiceMode('tankmen_bp15_6', 'tankmen_bp15_6', lang='SV', icon='tankmen_bp15_6'),
    VoiceMode('tankmen_bp15_7', 'tankmen_bp15_7', lang='SV', icon='tankmen_bp15_7'),
    VoiceMode('tankmen_bp15_8', 'tankmen_bp15_8', lang='SV', female=True, icon='tankmen_bp15_8'),
    VoiceMode('tankmen_bp15_9', 'tankmen_bp15_9', lang='SV', icon='tankmen_bp15_9'),
    VoiceMode('tankmen_bp16_5', 'tankmen_bp16_5', lang='UK', icon='tankmen_bp16_5'),
    VoiceMode('tankmen_bp16_6', 'tankmen_bp16_6', lang='UK', icon='tankmen_bp16_6'),
    VoiceMode('tankmen_bp16_7', 'tankmen_bp16_7', lang='UK', icon='tankmen_bp16_7'),
    VoiceMode('tankmen_bp16_8', 'tankmen_bp16_8', lang='UK', female=True, icon='tankmen_bp16_8'),
    VoiceMode('tankmen_bp16_9', 'tankmen_bp16_9', lang='UK', icon='tankmen_bp16_9'),
    VoiceMode('tankmen_bp17_5', 'tankmen_bp17_5', lang='EN', icon='tankmen_bp17_5'),
    VoiceMode('tankmen_bp17_8', 'tankmen_bp17_8', lang='UK', female=True, icon='tankmen_bp17_8'),
    VoiceMode('tankmen_mtlb1_1', 'tankmen_mtlb1_1', lang='ZH_CH', icon='tankmen_mtlb1_1'),
    VoiceMode('MartyVole', 'MartyVole', lang='DE', icon='Marty_Vole'),
    VoiceMode('cygan', 'cygan', lang='PL', icon='polish_commander'),
    VoiceMode('kirk', 'kirk', icon='cosm02_Kirk'),
    VoiceMode('spock', 'spock', icon='cosm02_Spock'),
    VoiceMode('uhura', 'uhura', female=True, icon='cosm02_Uhura'),
    VoiceMode('gup_erika', 'gup_erika', lang='DE', female=True, icon='girls_und_panzer_erika'),
    VoiceMode('gup_mika', 'gup_mika', lang='JA', female=True, icon='girls_und_panzer_mika'),
    VoiceMode('gup_crew_24', 'gup_crew_24', lang='JA', female=True, icon=['girls_und_panzer_aki', 'girls_und_panzer_mikko']),
    VoiceMode('gup_alice', 'gup_alice', lang='EN', female=True, icon='girls_und_panzer_alice'),
    VoiceMode('gup_darjeeling', 'gup_darjeeling', lang='UK', female=True, icon='girls_und_panzer_darjeeling'),
    VoiceMode('gup_crew_25', 'gup_crew_25', lang='UK', female=True, icon=['girls_und_panzer_orange', 'girls_und_panzer_assam', 'girls_und_panzer_rosehip', 'girls_und_panzer_rukuriri']),
    VoiceMode('ermelinda24_en', 'ermelinda24_en', lang='EN', female=True, icon='wt_2024_ermelinda'),
    VoiceMode('ermelinda24_cn', 'ermelinda24_cn', lang='ZH_CH', female=True, icon='wt_2024_ermelinda'),
    VoiceMode('krieger24_en', 'krieger24_en', lang='EN', icon='wt_2024_vonkrieger'),
    VoiceMode('krieger24_cn', 'krieger24_cn', lang='ZH_CH', icon='wt_2024_vonkrieger'),
    VoiceMode('mouzAkrobat24', 'mouzAkrobat24', lang='DE', icon='wt_2024_mouzakrobat'),
    VoiceMode('quickyBaby24', 'quickyBaby24', lang='UK', icon='wt_2024_quickybaby'),
    VoiceMode('dakillzor24', 'dakillzor24', lang='FR', icon='wt_2024_dakillzor'),
    VoiceMode('skill4ltu24', 'skill4ltu24', lang='RU', icon='wt_2024_skill4ltu'),
    VoiceMode('zhongPengFei24', 'zhongPengFei24', lang='ZH_CH', icon='wt_CN2024_zhongpengfei'),
    VoiceMode('bMeng24', 'bMeng24', lang='ZH_CH', icon='wt_CN2024_bmeng'),
    VoiceMode('yiTuanTuan24', 'yiTuanTuan24', lang='ZH_CH', female=True, icon='wt_CN2024_yituantuan'),
    VoiceMode('saoNian24', 'saoNian24', lang='ZH_CH', icon='wt_CN2024_saonian'),
]


MUSIC_MODES = [
    MusicMode('default', 'default'),
    MusicMode('offspring', 'offspringArenaMusic'),
    MusicMode('sabaton', 'sabatonArenaMusic'),
]
