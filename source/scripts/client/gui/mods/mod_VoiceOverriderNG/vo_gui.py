# -*- coding: utf-8 -*-

import random

import GUI
from gui.impl import backport
from gui.impl.gen import R

from gui.mods.gambiter import g_guiFlash
from gui.mods.gambiter.flash import COMPONENT_ALIGN as GF_ALIGN, COMPONENT_TYPE as GF_TYPE, COMPONENT_EVENT as GF_EVENT

from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_NOTE, LOG_WARNING


ICON_WIDTH = 158
ICON_HEIGHT = 118


def _getDynRes(res, path):
    comps = path.split('/', 1)
    if len(comps) == 1:
        return res.dyn(path)
    return _getDynRes(res.dyn(comps[0]), comps[1])


class VoGUI(object):
    def __init__(self, ID, updatePositionHook):
        self.ID = str(ID)
        self._visible = True
        self._updatePositionHook = updatePositionHook

        self.ID_flag = self.ID + '.flag'
        self.ID_icon = self.ID + '.icon'
        self.ID_label = self.ID + '.label'

        g_guiFlash.createComponent(self.ID, GF_TYPE.PANEL, {
            'x': 0, 'y': 0,
            'alignX': GF_ALIGN.LEFT, 'alignY': GF_ALIGN.TOP,
            'autoSize': True, 'limit': True, 'drag': True
        })
        g_guiFlash.createComponent(self.ID_flag, GF_TYPE.IMAGE, {
            'x': 0, 'y': 0, 'width': ICON_WIDTH, 'height': ICON_HEIGHT,
            'alignX': GF_ALIGN.LEFT, 'alignY': GF_ALIGN.TOP,
            'limit': True
        })
        g_guiFlash.createComponent(self.ID_icon, GF_TYPE.IMAGE, {
            'x': 0, 'y': 0, 'width': ICON_WIDTH, 'height': ICON_HEIGHT,
            'alignX': GF_ALIGN.LEFT, 'alignY': GF_ALIGN.TOP,
            'autoSize': True, 'limit': True
        })
        g_guiFlash.createComponent(self.ID_label, GF_TYPE.LABEL, {
            'x': ICON_WIDTH // 2, 'y': ICON_HEIGHT, 'width': ICON_WIDTH,
            'alignX': GF_ALIGN.CENTER, 'alignY': GF_ALIGN.BOTTOM,
            'autoSize': True, 'isHtml': True, 'limit': False
        })

        GF_EVENT.UPDATED += self._onUpdatePosition


    def destroy(self):
        GF_EVENT.UPDATED -= self._onUpdatePosition
        g_guiFlash.deleteComponent(self.ID_icon)
        g_guiFlash.deleteComponent(self.ID_flag)
        g_guiFlash.deleteComponent(self.ID_label)
        g_guiFlash.deleteComponent(self.ID)


    def visible(self, is_visible, params=None):
        if is_visible == self._visible:
            return

        self._visible = is_visible
        alpha = 1.0 if is_visible else 0.0
        g_guiFlash.updateComponent(self.ID, {'visible': is_visible, 'alpha': alpha}, params)


    def setPosition(self, req_x=-1, req_y=-1):
        screenWidth, screenHeight = GUI.screenResolution()
        x = req_x
        y = req_y

        if req_x < 0: # default value requested
            x = screenWidth // 4

        if req_y < 0: # default value requested
            y = screenHeight - ICON_HEIGHT

        if x + ICON_WIDTH > screenWidth:
            x = screenWidth - ICON_WIDTH

        if y + ICON_HEIGHT > screenHeight:
            y = screenHeight - ICON_HEIGHT

        if x != req_x or y != req_y:
            self._updatePositionHook(x, y)

        g_guiFlash.updateComponent(self.ID, {'x': x, 'y': y})


    def _onUpdatePosition(self, ID, options):
        if str(ID) != self.ID:
            return
        x = options.get('x')
        y = options.get('y')
        if x is not None and y is not None:
            self._updatePositionHook(x, y)


    def setCommander(self, voice_mode):
        flag = voice_mode.get_flag()
        if flag is None:
            g_guiFlash.updateComponent(self.ID_flag, {'visible': False})
        else:
            g_guiFlash.updateComponent(self.ID_flag, {'visible': True, 'image': flag.big_url})

        icon = voice_mode.get_icon()
        if type(icon) == list:
            icon = icon[random.randint(0, len(icon) - 1)]
        if icon is None or type(icon) != str or icon == '':
            icon = 'girl_empty' if voice_mode.female else 'tankman'

        res = _getDynRes(R.images.gui.maps.icons.tankmen.icons.big, icon)
        image_url = backport.image(res())

        label = voice_mode.get_label(short=True)
        text = '<p><font face="$FieldFont" size="16" color="#FFFFFF">' + label + '</font></p>'

        g_guiFlash.updateComponent(self.ID_icon, {'image': image_url})
        g_guiFlash.updateComponent(self.ID_label, {'text': text})
