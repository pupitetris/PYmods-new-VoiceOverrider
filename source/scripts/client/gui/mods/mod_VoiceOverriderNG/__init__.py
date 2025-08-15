__modID__ = '%(mod_ID)s'
__date__ = '%(file_compile_date)s'
__version__ = '2.0.2 ' + __date__

from gui.battle_control import avatar_getter
from gui.game_control.special_sound_ctrl import SpecialSoundCtrl
from items.vehicles import VehicleDescr
import nations

from OpenModsCore import Analytics, overrideMethod

from .config_interface import ConfigInterface
from .vo_gui import VoGUI


g_config = ConfigInterface()
g_gui = VoGUI(__modID__)
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

    self._SpecialSoundCtrl__arenaMusicSetup = musicSetup = arena.arenaType.wwmusicSetup.copy()
    tag = g_config.music_modes[g_config.data['music']].tag
    musicSetup.update(self._SpecialSoundCtrl__arenaMusicByStyle.get(tag, ()))
