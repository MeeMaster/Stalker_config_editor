# Stalker_config_editor
As of now, the only option is to modify item properties, however I am working on additional functionality, such as trade and crafting modification.
To load configs, go to `File->Open` and then select the folder with your unpacked STALKER .db files

Next, you will see the list of items on the left side, after you selected a subcategory.After clicking an item, a display will be shown for items properties.

You can modify all item properties here, however the ones shown here are the most commonly modified ones. There are also limits for sliders. The limits for armor are in line with in-game limitations on these values. For artifacts and food, the limits set are arbitrary.
If you wish to modify other properties or exceed the limits placed, you need to switch to full view.

When you switch the simple view off, you will see all properties for the item:

You can then modify the properties here, however be careful, as inputting wrong values may crash the game.

When you are finished with editing, save the changes by choosing `File->Save` or hitting `Ctrl+S`. 
You will get another save prompt, where you should select a directory, where all the changes will be saved. The directory structure of the saved files will be preserved. It is preferable, that you create a new directory for those modified files or make a backup of your unpacked files.
The project is still WIP and some bugs may be present. Please report your suggestions and all the bugs you encounter at https://github.com/MeeMaster/Stalker_config_editor/issues

In the nearest future I intend to add crafting modification (modify recipes, disassembly products etc.) and trade modification (Prices, item availability, discounts etc.)
