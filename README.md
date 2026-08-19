# Storage for World of Tanks mods

This repo is a Fork of Yury Polyacov's PYmods original, meant to publish my new version for mod_VoiceOverrider which includes new features and updates/fixes.

## ![VoiceOverriderNG][cover]

"New Generation" for VoiceOverrider, renamed so the overhauled version doesn't collide with the OG VoiceOverrider. This mod has been accepted in the [wgmods registry](https://wgmods.net/7288/) and is being included in [Aslain's Modpack](https://aslain.com/) (see the [forum topic](https://aslain.com/index.php?/topic/34501-mod-overhaul-voiceoverrider/)).

### Enhancements

* **Feature**: Instead of allowing to chose only one voice that will be globally used on every battle, allow for the use of up to 20 alternative voices, which are changed randomly before every battle. The selection uses a user-provided weight distribution, all configurable in-game so you can have certain voices more often than others.
* **Feature**: The national voice for each country can be manually selected as a voice option.
* **Feature**: Special voice selections and filters: 
  * **"Mute (No voice)"**: no voices at all
  * **Random**: get random female, male or either voices
  * **Sequential**: a "Round Robin" mode that instead of choosing at random, sequentially selects every available voice.
  * **Default/National: male/female**: use default voices or limit the voice selection to those consistent with the playing tank's nation.
* **Feature**: Option to not override the commander's voice if it has its own voice (meaning, only change the voice if the commander is "generic").
* **Feature**: Use the game's internals to probe available voices and add those missing from VoiceOverrider's list, allowing for newly added voices or those available from other voice mods to appear at the end of the selector lists even if they have not been manually added to the mod (some minor internal data needs to be worked on to provide a character label and link its corresponding portrait).
* **Feature**: To make it easier to find the desired voice, options are now better grouped and sorted, and are graphically marked with a flag of the language/country they belong to, plus a female mark if it is the case.
* **Enhancement**: Better grouping for "bloggers", or community leaders, so they can be found more easily. Some voices were grouped using prefixes that are a bit cryptic so they were removed or simplified or sent to the end of the string so they don't affect grouping.
* **Update**: (from the last published version from PYmods repo) Support all of the voices included up to 2.3.1.2 (latest as of 19/08/2026)


![Configuration Interface Screenshot][config_interface]

* **Feature**: Sometimes a voice may sound cool but we don't know to which commander it belongs. An icon with the portrait of the active commander can be enabled, featuring to which voice you are listening. You can drag the icon around and put it wherever you find it convenient. It can be disabled from the configuration screen if you find it clutters the screen.
* **Enhancement**: There's an option that allows to show the commander's portrait only while a special key is pressed (such as Alt, the default).

![In-Battle Portrait Screenshot][vo_gui]

### TO-DOs

* **Feature**: In-battle re-roll of the current voice.
* **Enhancement**: a small version of the in-battle commander portrait using the barracks icons, in case the "big" icon version is deemed too intrusive.
* **Enhancement**: For the "Do nothing (No override)" mode, show the actual commander's portrait during the battle.
* **Feature**: New overriding method: be able to select a voice for a given tank.
* **Feature**: Overriding with a given voice uppon meeting certain conditions, such as a specific voice, nation or genre (male/female)
* **Enhancement**: include voiceover banks of voices not available on all regions (such as HandOfBlood).
* **Bug**: There is a bug where playing the National voices may cause further attempts to play voices to not work. Only affects the configuration screen, voices still work throughout the game.
* **Help needed**: Translations to other languages would be greatly appreciated.
* **WoT bug**: Some voices are not correctly configured in the game. These have been disabled as their sound banks are not available (at least in the NA client). As a workaround and to have them active on clients that do provide these sound banks, a routine that checks the existence of the voiceover.bnk files at initialization is needed.
  * Disabled voices:
	* `HandOfBlood`: available only on the EU client, [apparently](https://worldoftanks.eu/en/news/specials/handofblood-commander-sale-mar23/).
	* `tankman_bp_12_m_10`: a Dune voice mode that points to the same female voice as `tankman_bp_12_m_5`
	* `valkyrie1`: Valkyria Chronicles: Welkin Gunther, probably [available only in the ASIA client](https://worldoftanks.asia/en/news/specials/ps-valkyria-chronicles-250123/).
	* `valkyrie2`: Valkyria Chronicles: Carisa Contzen, ditto.
    * `krieger24_cn`, `ermelinda24_cn`, `bMeng24`, `saoNian24`, `yiTuanTuan24`, `zhongPengFei24`: chinese voiceovers for Waffentrager 2024, probably [available only in the ASIA client](https://wotgame.cn/zh-cn/content/guide/general/waffentrager-event/).

### Usage

#### Installation

* Download the `mod_VoiceOverriderNG-v2-xxx.zip` file from the Releases section.
* Unzip content into the `mods` directory of your World of Tanks installation.

#### Configuration access

* Run the game
* Open the configuration window by clickinng on the lower-left **`◊◊`** mods button and then on **PYmods**

#### Default voice override

* As in the original VoiceOverrider, you will find a first voice selector, the Default, where you can use this to set a global override.
  * For the original global override to take effect, the selectors bellow for the alternative voices must all have a weight of 0

#### Alternative voices

* If you want up to 21 alternative voices to be selected randomly for each battle, select the voices on the left column, and the weights on the right.
* Weights work this way:
  * TLDR: just give more weight to those you really like and want to come up more often, and be careful not to go too low on those you don't want that often because the chance they appear may become way low and you may almost never hear them.
  * the probability of an alternative voice to be used on a given battle is `weight_sum / voice_weight`, so for example:
    * if all voices have the same weight, the chance of any of them to be selected is the same for all.
    * a weight of 0 means no chance, so that deactivates that option.
    * if you have two voices with a weight of 10, three with 5, five with 1 and the rest with 0, the chances will be:
      * sum of weights: `2 * 10 + 3 * 5 + 5 * 1 = 40`
      * chances: `10/40, 10/40, 5/40, 5/40, 5/40, 1/40, 1/40, 1/40, 1/40, 1/40`
      * chances (simplified): `1/4, 1/4, 1/8, 1/8, 1/8, 1/40, 1/40, 1/40, 1/40, 1/40`
      * chances (percent): `25%, 25%, 12.5%, 12.5%, 12.5%, 2.5%, 2.5%, 2.5%, 2.5%, 2.5%`

## Original PYmods Notes

Storage for World of Tanks mods.
---
This repo is provided as an archive of my mods' source code with the attached history of 15-year-old me's coding prowess :)  
Feel free to fork the repo and update/upgrade/support the mods however you see fit. A `(thx to Polyacov_Yury)` in startup python.log message(s) is appreciated.

Notable forks:
- https://github.com/pupitetris/PYmods-new-VoiceOverrider/ - awesome rework/upgrade of VoiceOverrider

Other projects (also in need of support):
- https://github.com/PolyacovYury/PYmods/wiki - (some) docs on the intricacies of the mods' internals
- https://github.com/PolyacovYury/ModPacker - data-driven modpack installer
- https://github.com/OpenMods-WoT/core/ (fka PYmodsCore) - some common APIs that greatly simplify mod creation by abstracting away boilerplate code
  - is a submodule in `core/` folder
- https://github.com/OpenMods-WoT/build_tools - a collection of automation tools that enables reproducible .pycs, .wotmods and .zips
  - is a submodule in `build_tools/` folder
- https://koreanrandom.com/forum/topic/44153- - central hub with links to other topics that also has screenshots and descriptions of some of the mods
---
After cloning, it is recommended to:
 - run `git submodule update --init --recursive`
 - copy all files in `build_tools/hooks` into `.git/hooks`
 - run `py -2 build_tools/mtimestore.py -r`
 - read and follow instructions in res/res/res.md file
otherwise correct building of the mods is not guaranteed.
```
build_data/
  archives/ - lists of files that need to be bundle-ified into mod archives
  wotmods/ - lists of files that need to be bundle-ified into .wotmod files
  debug_targets.txt - list of local folders that need to receive freshly-built wotmod files for testing
  GAME_VERSION - contains the version of the game client that will be baked into mod archives by build_tools/release.cmd
  release_targets.txt - list of local folders that need to receive freshly-built mod archives for upload to file shares
build_tools/
  hooks/ - git hooks that simplify working with the repo by automagically starting debug.cmd and release.cmd when appropriate
  compiler.py - my modification of standard compileall which uses git calls to retrieve commit dates
  debug.cmd - launch to compile all sources into .pyc, then pack .pyc into .wotmods
  mtimestore.py - my implementation of kareltucek's git-mtime-extension, also made it more versatile
  packer.py - archive and wotmod packer
  release.cmd - launch to pack all .wotmods and assets into .zip archives for publishing
core/ - OpenModsCore source code, used for IDE code discovery
res/
  configs/ - folder for mods' configs
  flash/ - source code for .swf components, also see swc.md
  img/ - images added to .zip archives
  meta/ - renamed into meta.xml for .wotmods that need it
  res/
    audioww/ - .bnk files for mods, see res.md
    Axes/ - model with the X/Y/Z axis pointers, used by LampLights
    gui/ - images added to .wotmods
    scripts/ - this should probably have been in the folder above...
    vehicles/ - models for remods for RemodEnabler, see res.md
    wotmods/ - pre-compiled mods by other authors used as API providers
source/scripts/
  /client:
    /gui/mods:
      /mod_CamoSelector - custom camouflage installer
      /mod_RemodEnabler - custom models dispatcher
      /mod_Skinner - custom skins dispatcher
      AsyncModLoader.py - makes it so that game client doesn't appear hanging while the mods are being loaded
      AsyncModLoader_init.py - part of AML, replacement of scripts/client/gui/mods/__init__.py
      mod_AimingAngles.py - horizontal and vertical aim limits on-screen
      mod_AllQuestsProgresses.py - forces quests' conditions from both campaigns to show up simultaneously
      mod_AppreciationBadges.py - adds custom badges to those who install the mod
      mod_BanksLoader.py - automatic installer for .bnk files
      mod_BigTextConsumablesPanel.py - large numbers in consumables panel achieved with pure Python
      mod_color_messages.py - colorizes battle result messages in the Service Channel 
      mod_CamoSelector.py - mod loader stub file for CamoSelector (won't be discovered without it)
      mod_DamagePercentIndicator.py - adds percentage of your full HP to incoming damage indicators
      mod_HangarBoosterViewer.py - (probably obsolete) shows active boosters and their remaining time
      mod_HangarCollision.py - (obsolete) used to show vehicle collision models in Hangar until WG removed them
      mod_HangarGUITweaks.py - some informativity tweaks to Hangar GUI
      mod_HangarScreenshots.py - hides GUI and locks camera position upon button press
      mod_Horns.py - plays horn sound and sends a message to chat upon button press
      mod_IngameGUITextTweaks.py - adds a vehicle class icon and strips out nicknames when needed
      mod_InsigniaOnGun.py - makes gun insignias appear on vehicles that don't deserve them yet
      mod_LampLights.py - allows to attach light sources and models onto tanks
      mod_LogSwapper.py - because placing log for received damage on the top of the screen was a smart move by WG
      mod_PermanentMusic.py - forces ingame music to play throughout the entire battle
      mod_PlayerHPAnnouncer.py - plays a sound when your HP drops below 50, 25 or 10%
      mod_PlayersPanelHP.py - well, the name is self-explanatory
      mod_PY_support_links.py - adds donation links to the mods' settings GUI. Feel free to ignore :3
      mod_RadialMenu.py - custom battle commands menu maker
      mod_RemodEnabler.py - mod loader stub file for RemodEnabler (won't be discovered without it)
      mod_ShowVehicle.py - displays your vehicle's hull and turret in sniper mode
      mod_ShutLoggersUp.py - makes python.log a little less cluttered
      mod_Skinner.py - mod loader stub file for Skinner (won't be discovered without it)
      mod_SoundEventInjector.py - an alternative to editing scipts/item_defs/vehicles/ for audio mod makers
      mod_StatPaints.py - paints vehicles depending on their driver's WGR value
      mod_UT_announcer.py - frag, some medals and battle time sound notifier
      mod_VMTFix.py - Vehicle Model Transparency Fix - because transparent elements don't display on player vehicle
      mod_VoiceOverriderNG.py - switches some switches in SoundGroups to make different voiceover versions appear
      PlayersPanelAPI.py - says on the tin. simplifies modification of team panels on sides of the screen
    /helpers/i18n:
      __init__.py - transforms helpers.i18n from a module to package and adds a mod loader to it
      _i18nDebugger.py - a simple localisation debugger
      ButtonReplacer.py - localisation editor, replacement to editing .mo files
      HangarPainter.py - hangar text colorizer
    /mods:
      __init__.py - stub file for client.mods package
      CameraNode.py - obsolete mod loader
```


[cover]: media/cover.png
[config_interface]: media/config_interface.png
[vo_gui]: media/vo_gui-2.2.png
