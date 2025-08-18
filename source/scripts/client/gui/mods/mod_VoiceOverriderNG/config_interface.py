# -*- coding: utf-8 -*-

from collections import namedtuple
import itertools
import random

import BigWorld
import Settings
import SoundGroups
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, LOG_WARNING
from gui.shared.personality import ServicesLocator

from OpenModsCore import SimpleConfigInterface

from .voice_mode import VoiceMode, VOICE_MODES, MUSIC_MODES, NATIONS, NATIONS_BY_LANG, NATIONS_AVAILABLE_NAMES
from .i18n import I18N


DEFAULT_POSITION = -1


def getInt(n, default):
    try:
        return int(float(n))
    except (ValueError, TypeError) as e:
        pass
    return default


class ConfigInterface(SimpleConfigInterface):
    VOICE_PREVIEW = itertools.cycle(('wwsound_mode_preview01', 'wwsound_mode_preview02', 'wwsound_mode_preview03'))
    NUM_VOICE_ALTS = 20


    def __init__(self):
        self._voice_enabled = True
        self._voice_labels = []
        self._previewSound = None
        self._previewNations = []

        self.voice_modes = []
        self._voice_modes_by_name = {}
        self._voice_modes_map = {}
        self.currentVoiceMode = None

        self.music_modes = MUSIC_MODES

        super(ConfigInterface, self).__init__()


    def _try_voice_mode(self, mode, mode_descs):
        res = mode.is_available(mode_descs)
        if not res is None:
            return res
        
        res = self.setSystemValue(mode_key=mode)
        LOG_NOTE('special: ', res, mode)
        return res


    # Iterate over keys that _try_voice_mode/is_available didn't remove from mode_descs:
    def _missing_mode_descs(self, mode_descs):
        missing_modes = []
        for name in sorted(mode_descs.keys()):
            if name[:4] == 'User':
                continue
            mode_desc = mode_descs[name]
            LOG_NOTE('adding: ', mode_desc)
            lang = mode_desc.voiceLanguage
            label = '+ ' + (lang if lang is not None and len(lang) > 0 else name)
            mode = VoiceMode(name, name, label=label)
            missing_modes.append(mode)
        return missing_modes


    def _set_voice_modes(self):
        mode_descs = { name: mode_desc for name, mode_desc in SoundGroups.g_instance.soundModes.modes.items() }
        VOICE_MODES.sort(key=lambda mode: self.i18n.get('UI_setting_voice_%s' % mode.name, mode.name))
        self.voice_modes = filter(lambda mode: self._try_voice_mode(mode, mode_descs), VOICE_MODES);
        self.voice_modes += self._missing_mode_descs(mode_descs)

        for idx, mode in enumerate(self.voice_modes):
            mode.idx = idx
        self._voice_labels = [ mode.get_label(self.i18n, with_gender=True) for mode in self.voice_modes ]
        self._voice_modes_by_name = { mode.name: mode for mode in self.voice_modes }


    def _set_default_voice_alt_conf(self):
        for i in range(0, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self.data['voiceAlt_' + num + '_sel'] = 0
            self.data['voiceAlt_' + num + '_name'] = 'nothing'
            self.data['voiceAlt_' + num + '_weight'] = 0
            self.i18n['UI_setting_voiceAlt_' + num + '_sel_text'] = None
            self.i18n['UI_setting_voiceAlt_' + num + '_weight_text'] = None

        self.data['voiceAlt_0_sel'] = 'DEFAULT'


    def init(self):
        self.ID = 'VoiceOverriderNG'
        self.i18n = I18N
        self.author = 'by Arturo Espinosa (overhaul) and Polyacov_Yury'
        self.version = '2.0.2 %(file_compile_date)s'
        self.modsGroup = 'PYmods'
        self.modSettingsID = 'PYmodsGUI'

        self.data = {
            'enabled': True,
            'icon_enabled': True,
            'icon_x': DEFAULT_POSITION,
            'icon_y': DEFAULT_POSITION,
            'music': 0,
            'voice': 0,
            'voice_name': '',
            'voice_use_tank_nation': False,
        }

        self._set_default_voice_alt_conf()
        super(ConfigInterface, self).init()
        self._set_voice_modes()


    def _data_voice_set_by_sel(self, sel_key, name_key, src=None):
        if src is None:
            src = self.data
        idx = src[sel_key]
        if idx < len(self.voice_modes):
            self.data[name_key] = self.voice_modes[idx].name


    def _data_voice_set_by_name(self, sel_key, name_key):
        if name_key in self.data: 
            name = self.data[name_key]
            if name in self._voice_modes_by_name:
                self.data[sel_key] = self._voice_modes_by_name[name].idx
                return
        self._data_voice_set_by_sel(sel_key, name_key)


    def readData(self, quiet=True):
        super(ConfigInterface, self).readData(quiet)

        self._data_voice_set_by_name('voice', 'voice_name')

        for i in range(1, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self._data_voice_set_by_name('voiceAlt_' + num + '_sel',
                                         'voiceAlt_' + num + '_name')
                    
                    
    def onApplySettings(self, settings):
        self._data_voice_set_by_sel('voice', 'voice_name', src=settings)

        for i in range(1, self.NUM_VOICE_ALTS + 1):
            num = str(i)
            self._data_voice_set_by_sel('voiceAlt_' + num + '_sel',
                                        'voiceAlt_' + num + '_name',
                                        src=settings)

        super(ConfigInterface, self).onApplySettings(settings)


    def createTemplate(self):
        column1 = [
            self.tb.createOptions(
                'voice',
                self._voice_labels,
                width=350,
                button={'iconSource': '../maps/icons/buttons/sound.png'}),
            self.tb.createControl('voice_use_tank_nation'),
            self.tb.createLabel('voiceAlt'),
            self.tb.createLabel('voiceAlt_0'),
        ]

        column2 = [
            self.tb.createOptions(
                'music', [self.i18n['UI_setting_music_%s' % music_mode.name] for music_mode in self.music_modes]),
            self.tb.createControl('icon_enabled'),
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
                    self._voice_labels,
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
            mode = self.selectAltVoiceMode(force=True)
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
            self._previewNations = list(NATIONS_AVAILABLE_NAMES)
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
            if female is None or mode.female == female:
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


    def _selectAltVoiceModeByWeight(self):
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
        

    def _selectAltVoiceMode(self, nation=None):
        nation = self._nation_canon(nation)

        retries = 1000
        while retries > 0:
            retries -= 1
            mode_idx = self._selectAltVoiceModeByWeight()
            mode = self.voice_modes[mode_idx]
            if self._mode_nation_elegible(nation, mode):
            	return mode
        return self.voice_modes[self.data['voice']]


    def selectAltVoiceMode(self, nation=None, force=False):
        if not force and self.currentVoiceMode is not None:
            return self.currentVoiceMode

        mode = self._selectAltVoiceMode(nation)
        if mode.name[:6] == 'random':
            mode = self.selectRandomMode(mode.name[7:], nation)
        if not force:
            self.currentVoiceMode = mode
        return mode


    def iconEnabled(self):
        return bool(self.data.get('icon_enabled', True))


    def iconGetPosition(self):
        return (getInt(self.data.get('icon_x'), DEFAULT_POSITION),
                getInt(self.data.get('icon_y'), DEFAULT_POSITION))


    def iconSetPosition(self, x, y):
        self.data['icon_x'] = getInt(x, DEFAULT_POSITION)
        self.data['icon_y'] = getInt(y, DEFAULT_POSITION)
