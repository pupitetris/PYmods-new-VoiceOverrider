# Storage for World of Tanks mods

This repo is a Fork of Yury Polyacov's PYmods original, meant to publish my new version for mod_VoiceOverrider which includes new features and updates/fixes.

## VoiceOverrider

### Enhancements

* **Feature**: Instead of allowing to chose only one voice that will be globally used on every battle, allow for the use of up to 20 alternative voices, which are changed randomly before every battle. The selection uses a user-provided weight distribution, all configurable in-game.
* **Feature**: Use the game's internals to probe available voices and add those missing from VoiceOverrider's list, allowing for newly added voices or other voice mod's to appear at the end of the list.
* **Feature**: Sorted voice options, making it easier to find the desired voice.
* **Feature**: Special voice options. "None (Silent)" option disables (mutes) the voices and "No Override" does not change the voice, respecting the voice that would normally be used in the battle.
* **Update**: Support all of the voices included up to 1.29.1.0 (latest as of 07/28/2025, includes Duke Nukem and Lara Croft)
* **Fixes**: Tweaks to voice names and removed typos.

### TO-DOs

* **Bug**: There is a bug where playing the National voices may cause further attempts to play voices to not work. Only affects the configuration screen, voices still work throughout the game.
* **Enhancement**: The voice of each nation appears at the end with the discovered voices, upgrade them to first-class and group them at the start of the lists.
* **Enhancement**: Better grouping for "bloggers", or community leaders, so they can be found easier. Some voices are grouped using prefixes that are a bit cryptic.
* **Help needed**: Russian translations have not been updated or checked for typos (help needed, I don't speak Russian).
* **WoT bug**: HandOfBlood, a voice in german that seems quite fun but is not available on the NA installation appears as an option because the NA configuration says it is included, but the bank file is not present.
* **Feature**: New overriding method: selecting a voice for a given tank
* **Feature**: Overriding with a given voice uppon meeting certain conditions, such as a specific voice, nation or genre (male/female)

### Usage

#### Installation

* Download the `mod_VoiceOverrider.zip` file from the Releases section.
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

```
source/scripts:
  compiler.py - my modification of standard compileall which uses git calls to retrieve commit dates
  generate_configs.py - build configs automagic generator
  mtimestore.py - my implementation of kareltucek's git-mtime-extension, also made it more versatile
  pack_wotmods.py - archive packer
  /client:
    /gui/mods:
      /mod_CamoSelector - custom camouflage installer
      /mod_RemodEnabler - custom models dispatcher
      /mod_Skinner - custom skins dispatcher
      mod_AppreciationBadges.py - adds custom badges to those who install the mod
      mod_BanksLoader.py - automatic installer for .bnk files
      mod_CamoSelector.py - mod loader stub file for CamoSelector
      mod_HangarScreenshots - hides GUI and blocks camera position changing upon button press
      mod_Horns.py - plays horn sound and sends a message to chat upon button press
      mod_IngameGUITextTweaks.py - adds a vehicle class icon and strips out nicknames when needed
      mod_InsigniaOnGun.py - makes gun insignias appear on vehicles that didn't deserve it yet
      mod_LampLights.py - allows to attach light sources and models onto tanks
      mod_LogSwapper.py - because placing log for received damage on the top of the screen was a smart move by WG
      mod_PlayerHPAnnouncer.py - plays a sound when your HP drops below 50, 25 or 10%
      mod_PlayersPanelHP.py - well, the name is self-explanatory
      mod_RadialMenu.py - custom battle commands menu maker
      mod_RemodEnabler.py - mod loader stub file for RemodEnabler
      mod_ShowVehicle.py - displays your vehicle's hull and turret in sniper mode
      mod_Skinner.py - mod loader stub file for Skinner
      mod_SoundEventInjector.py - an alternative to editing scipts/item_defs/vehicles/ for audio mod makers
      mod_StatPaints.py - paints vehicles depending on their driver's WGR value
      mod_UT_announcer.py - frag, some medals and battle time sound notifier
      mod_VMTFix.py - Vehicle Model Transparency Fix - because transparent elements don't display on player vehicle
      mod_VoiceOverrider.py - switches some switches in SoundGroups to make different voiceover versions appear
    /helpers/i18n:
      __init__.py - transforms helpers.i18n from a module to package and adds a mod loader to it
      _i18nDebugger.py - a simple localisation debugger
      ButtonReplacer.py - localisation editor, replacement to editing .mo files
      HangarPainter.py - hangar text colorizer
    /mods:
      __init__.py - stub file for client.mods package
      CameraNode.py - obsolete mod loader
```
After cloning, it is recommended to:
 - copy all files in `build_tools/hooks` into `.git/hooks`
 - run `py -2 build_tools/mtimestore.py -r`
 - read and follow instructions in res/res/res.md file
otherwise correct building of the mods is not guaranteed.
