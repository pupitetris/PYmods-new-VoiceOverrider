__modID__ = '%(mod_ID)s'
__date__ = '%(file_compile_date)s'
__version__ = '2.1.0 ' + __date__

from gui.battle_control import avatar_getter
from gui.game_control.special_sound_ctrl import SpecialSoundCtrl
from gui.Scaleform.daapi.view.meta import DamagePanelMeta
from items.vehicles import VehicleDescr
import nations

from OpenModsCore import Analytics, overrideMethod, events
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, LOG_WARNING

from .config_interface import ConfigInterface
from .vo_gui import VoGUI


g_config = ConfigInterface()
#analytics = Analytics(g_config.ID, g_config.version, 'UA-76792179-22')


g_gui = None


@overrideMethod(SpecialSoundCtrl, 'setPlayerVehicle')
def new_setPlayerVehicle(base, self, vehiclePublicInfo, isPlayerVehicle, *args, **kwargs):
    global g_gui

    base(self, vehiclePublicInfo, isPlayerVehicle, *args, **kwargs)
    arena = avatar_getter.getArena()
    if not g_config.data['enabled'] or arena is None:
        return

    nation = nations.NAMES[VehicleDescr(vehiclePublicInfo.compDescr).type.id[0]]
    voice_mode = g_config.selectAltVoiceMode(nation)
    g_config.setSystemValue(nation, voice_mode)

    if g_gui is not None:
        g_gui.setCommander(voice_mode)

    self._SpecialSoundCtrl__arenaMusicSetup = musicSetup = arena.arenaType.wwmusicSetup.copy()
    tag = g_config.music_modes[g_config.data['music']].tag
    musicSetup.update(self._SpecialSoundCtrl__arenaMusicByStyle.get(tag, ()))


@events.PlayerAvatar.startGUI.after
def on_startGUI(*_, **__):
    global g_gui
    global g_config

    if not g_config.data['enabled'] or not g_config.iconEnabled():
        return

    (x, y) = g_config.iconGetPosition()

    if g_gui is None:
        g_gui = VoGUI(__modID__, g_config.iconSetPosition)

    g_gui.setPosition(x, y)

    voice_mode = g_config.currentVoiceMode
    g_gui.setCommander(voice_mode)
    g_gui.visible(True)


@events.PlayerAvatar.destroyGUI.before
def on_destroyGUI(*_, **__):
    global g_gui
    global g_config

    if not g_config.data['enabled']:
        return

    g_config.currentVoiceMode = None

    if not g_config.iconEnabled() or g_gui is None:
        return

    g_gui.visible(False)
    g_gui.destroy()
    del g_gui
    g_gui = None

    g_config.writeDataJson()


@overrideMethod(DamagePanelMeta.DamagePanelMeta, 'as_setVehicleDestroyedS')
def new_onVehicleDestroyed(base, self, *args, **kwargs):
    global g_gui
    global g_config

    if g_config.data['enabled'] and g_config.iconEnabled():
        g_gui.visible(False, {'delay': 3.0, 'duration': 0.5})

    return base(self, *args, **kwargs)
