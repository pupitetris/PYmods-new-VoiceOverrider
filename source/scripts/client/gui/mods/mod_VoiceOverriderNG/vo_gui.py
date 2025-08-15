from gui.mods.gambiter import g_guiFlash
from gui.mods.gambiter.flash import COMPONENT_ALIGN as GF_ALIGN, COMPONENT_TYPE as GF_TYPE


class VoGUI(object):
    def __init__(self, ID):
        self.ID = str(ID)
        g_guiFlash.createComponent(self.ID, GF_TYPE.PANEL, {
            'x': 0, 'y': 0, 'alignX': GF_ALIGN.CENTER, 'alignY': GF_ALIGN.CENTER, 'width': 0, 'height': 0, 'limit': False})
        g_guiFlash.createComponent(self.ID + '.icon', GF_TYPE.IMAGE, {
            'alignX': GF_ALIGN.CENTER, 'alignY': GF_ALIGN.CENTER, 'limit': False})
        g_guiFlash.createComponent(self.ID + '.name', GF_TYPE.LABEL, {
            'alignX': GF_ALIGN.CENTER, 'alignY': GF_ALIGN.CENTER, 'limit': False})
