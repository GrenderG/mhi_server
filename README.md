# mhi_server

## About the Files

Due to space limitations in the original MHi game, many resources were downloaded from CAPCOM's servers during gameplay. These downloaded resources include:

- **pcX_gard_YY.mbac**: This file contains the model data for the currently equipped armor and all 3D weapon models for the given type (e.g., Sword & Shield, Greatsword, Lance, Hammer, Bowgun). "X" represents the weapon type, and "YY" is the armor index.
- **m_pcX.mtra**: This file contains all animations for a given weapon type.
- **gard_YY.bmp**: This is the .bmp texture for the currently equipped armor.
- **arm_ZZ.bmp:** This is the .bmp texture for the currently equipped weapon.

Due to this, recovering original assets is a very difficult task.

The `recreated` folder contains community-made approximations of missing files. As more original saves become available, we'll replace these with authentic assets.

## Included Flask Server

The repository includes a Python Flask server (`mhi_server.py`) that:

- Serves files from both `original_dumps` and `recreated` folders.
- Prioritizes original files when available.
- Implements placeholder functionality for `pcX_gard_YY.dat` requests.
- Emulates several original server endpoints.

## Getting Started

1. Clone this repository.
2. Copy `config.ini.dist` to `config.ini` and edit as needed.
3. Place your files in the appropriate data subfolders.
4. Run the server: `python mhi_server.py`.

## Notes
Textures are .bmp files with an 8-bit color depth and use a 96-color indexed palette (we tried 256, but they didn't work; 128 worked sometimes) If you're using GIMP, make sure to enable "Do not write color space information" under "Compatibility Options" when exporting the file. If using Photoshop make sure Palette is set to "Local (Perceptual)", Colors to "96", Forced to "Black and White", Transparency disabled, Matte to "None", Dither to "Diffusion", Amount to "75%" and Preserve Exact Colors is disabled.

Armor textures are easy to test using [PVMicro](https://github.com/j2me-preservation/MascotCapsule/raw/refs/heads/master/Docs_Resources_SDK/pvmicro_v5_0.zip). Open PVMicro (launch the "E" version for English), load the .mbac file, then the .mtra file, and then your gard_YY.bmp file. You can edit the image and save, and PVMicro will update automatically.

## Credits & Acknowledgments

- Some unused logic taken from [Yuvi-App/Keitai-Servers](https://github.com/Yuvi-App/Keitai-Servers).
- MHi file packer/unpacker from [Sin365/MHiRepacker](https://github.com/Sin365/MHiRepacker).
- [Keitai Wiki community](https://keitaiwiki.com) for their preservation efforts.

## Join the Effort

For more information or to contribute:
- Join the Keitai Wiki Discord: [https://discord.gg/tWUYbF3N9F](https://discord.gg/tWUYbF3N9F)
- Contribute original save files.
- Help recreate missing assets.
- Help research the .mbac and .mtra formats.

## License

This project is shared for educational and preservation purposes under **GPLv3 License**. All original assets belong to their rightful owners.