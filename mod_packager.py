#!/usr/bin/env python3

"""
Mod Packager for Bullseye Injector

This module handles packaging processed sprites into ready-to-go mod files
for various game modding platforms.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

class ModPackager:
    """Handles packaging sprites into mod files."""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.supported_formats = ['.mod', '.zip']
    
    def create_mod_package(self, 
                          source_dir: Path,
                          output_dir: Path, 
                          mod_name: str,
                          mod_version: str = "1.0",
                          mod_author: str = "Bullseye Injector",
                          mod_description: str = "Generated sprite mod",
                          target_game: str = "Pokemon",
                          sprite_scale_data: Dict[str, Tuple[int, int]] = None,
                          custom_scaling: Dict[str, float] = None,
                          replacement_sprite_names: set = None,
                          create_summary_table: bool = True,
                          create_front_table: bool = True,
                          create_back_table: bool = True,
                          use_mod_zip_extension: bool = False) -> Path:
        """
        Create a complete mod package from processed sprites.
        
        Args:
            source_dir: Directory containing processed sprites
            output_dir: Directory where the final .mod file should be placed
            mod_name: Name of the mod
            mod_version: Version of the mod
            mod_author: Author of the mod
            mod_description: Description of the mod
            target_game: Target game for the mod
            sprite_scale_data: Dictionary of sprite canvas sizes
            custom_scaling: Custom scaling configuration
            replacement_sprite_names: Set of replacement sprite filenames (only these get scale entries)
            use_mod_zip_extension: If True, output as .mod.zip instead of .mod
            
        Returns:
            Path to the created mod file
        """
        try:
            # Sanitize mod name and description for safe use
            safe_mod_name = self._sanitize_mod_name(mod_name)
            safe_mod_description = self._sanitize_mod_description(mod_description)
            
            self.logger.info(f"🔧 Creating mod directory with sanitized name: '{safe_mod_name}'")
            
            # Create working directory for mod structure
            try:
                working_dir = Path(tempfile.mkdtemp(prefix=f"mod_{safe_mod_name}_"))
            except Exception as e:
                self.logger.error(f"❌ Failed to create working directory: {e}")
                raise
            
            mod_dir = working_dir / safe_mod_name
            
            # Create mod directory structure
            try:
                mod_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                self.logger.error(f"❌ Failed to create mod directory '{mod_dir}': {e}")
                raise
            
            # Copy processed sprites to mod directory
            self._copy_sprites_to_mod(source_dir, mod_dir, sprite_scale_data, custom_scaling, replacement_sprite_names,
                                     create_summary_table, create_front_table, create_back_table)
            
            # Create mod metadata
            self._create_mod_metadata(mod_dir, safe_mod_name, mod_version, mod_author, safe_mod_description, target_game)
            
            # Package the mod
            mod_file = self._package_mod(mod_dir, safe_mod_name, use_mod_zip_extension)
            
            # Move mod file to output directory
            final_mod_path = output_dir / mod_file.name
            
            # Ensure output directory exists
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if a directory with the same name exists and remove it
            if final_mod_path.is_dir():
                self.logger.warning(f"⚠️ Directory with same name as mod file exists: {final_mod_path} - removing it")
                shutil.rmtree(final_mod_path)
            elif final_mod_path.is_file():
                # Remove existing file if it exists
                final_mod_path.unlink()
            
            # Move the file with error handling
            try:
                shutil.move(str(mod_file), str(final_mod_path))
                
                # Verify the file exists as a file (not a directory)
                if not final_mod_path.is_file():
                    raise FileNotFoundError(f"Mod file not found after move: {final_mod_path}")
                    
                self.logger.info(f"📊 Final mod file size: {final_mod_path.stat().st_size} bytes")
                
            except Exception as move_error:
                self.logger.error(f"❌ Failed to move mod file: {move_error}")
                raise
            
            # Clean up working directory
            shutil.rmtree(working_dir)
            
            return final_mod_path
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create mod package: {e}")
            raise
    
    def _copy_sprites_to_mod(self, source_dir: Path, mod_dir: Path, sprite_scale_data: Dict[str, Tuple[int, int]] = None, custom_scaling: Dict[str, float] = None, replacement_sprite_names: set = None, create_summary_table: bool = True, create_front_table: bool = True, create_back_table: bool = True):
        """Copy processed sprites to the mod directory structure and update scaling tables."""
        # Create the standard mod directory structure matching the extracted format
        battlesprites_dir = mod_dir / "sprites" / "battlesprites"
        battlesprites_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy all GIF and PNG files from output directory to battlesprites subdirectory
        gif_files = list(source_dir.glob("*.gif"))
        png_files = list(source_dir.glob("*.png"))
        all_sprite_files = gif_files + png_files
        
        # Track which Pokemon IDs were processed (for scaling tables)
        # Only track IDs for sprites that are actual replacements, not Bullseye originals
        processed_pokemon_ids = {'front': set(), 'back': set(), 'all': set()}
        
        for i, sprite_file in enumerate(all_sprite_files):
            dest_file = battlesprites_dir / sprite_file.name
            shutil.copy2(sprite_file, dest_file)
            
            # Only track Pokemon IDs for replacement sprites
            if replacement_sprite_names and sprite_file.name in replacement_sprite_names:
                # Extract Pokemon ID from filename (e.g., "001-front-n.gif" -> "001")
                match = re.match(r'^(\d+)-', sprite_file.name)
                if match:
                    pokemon_id = match.group(1)
                    processed_pokemon_ids['all'].add(pokemon_id)
                    
                    # Categorize as front or back
                    if '-back-' in sprite_file.name.lower():
                        processed_pokemon_ids['back'].add(pokemon_id)
                    else:
                        processed_pokemon_ids['front'].add(pokemon_id)
            
            # Log progress every 100 files or for the first and last few files
            if (i + 1) % 100 == 0 or i < 5 or i >= len(all_sprite_files) - 5:
                self.logger.info(f"📁 Copied sprite: {sprite_file.name}")
        
        self.logger.info(f"📦 Packaged {len(all_sprite_files)} sprites into mod")
        
        # Always create scaling tables (even if empty) to maintain mod structure
        # sprite_scale_data may be empty in Shiny Hunter mode, but tables should still exist
        self._create_and_update_scaling_tables(mod_dir, sprite_scale_data, custom_scaling, processed_pokemon_ids,
                                              create_summary_table, create_front_table, create_back_table)
    
    def _create_and_update_scaling_tables(self, mod_dir: Path, sprite_scale_data: Dict[str, Tuple[int, int]] = None, custom_scaling: Dict[str, float] = None, processed_pokemon_ids: Dict[str, set] = None, create_summary_table: bool = True, create_front_table: bool = True, create_back_table: bool = True):
        """Create scaling table files with custom values and copy them to mod directory."""
        try:
            # sprite_scale_data may be None or empty (e.g., in Shiny Hunter mode)
            # Always create tables to maintain mod structure, even if they're mostly empty
            if sprite_scale_data is None:
                sprite_scale_data = {}
                self.logger.info("📊 No sprite scale data available (may be in Shiny Hunter mode) - creating empty scaling tables")
            
            # Look for modpackages directory to get original headers
            script_dir = Path(__file__).parent
            
            # Check if we're running as a packaged executable (PyInstaller)
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                # Running as packaged executable - look in the temp directory first
                temp_dir = Path(sys._MEIPASS)
                modpackages_source = temp_dir / "modpackages"
            else:
                # Running as development script
                modpackages_source = script_dir / "modpackages"
            
            # Create temporary directory for scaling files
            temp_dir = Path(tempfile.mkdtemp())
            
            try:
                # Create the scaling files with custom values
                self._create_scaling_files_with_custom_values(temp_dir, modpackages_source, sprite_scale_data, custom_scaling, processed_pokemon_ids, create_summary_table, create_front_table, create_back_table)
                
                # Copy the created scaling files to the mod directory
                scaling_files = [
                    "table-summary-scale.txt",
                    "table-front-scale.txt", 
                    "table-back-scale.txt"
                ]
                
                for filename in scaling_files:
                    source_file = temp_dir / filename
                    dest_file = mod_dir / "sprites" / "battlesprites" / filename
                    
                    if source_file.exists():
                        shutil.copy2(source_file, dest_file)
                        self.logger.info(f"📄 Created and copied scaling table: {filename}")
                    else:
                        self.logger.warning(f"⚠️ Scaling table not created in temp dir: {filename} (expected at {source_file})")
                
                # Copy icon.png from modpackages to the mod directory
                icon_source = modpackages_source / "icon.png"
                if icon_source.exists():
                    icon_dest = mod_dir / "icon.png"
                    shutil.copy2(icon_source, icon_dest)
                    self.logger.info(f"📦 Copied icon.png: {icon_dest}")
                else:
                    self.logger.warning(f"⚠️ Icon file not found: {icon_source}")
                
            finally:
                # Clean up temporary directory
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create and copy scaling table files: {e}")
    
    def _create_scaling_files_with_custom_values(self, temp_dir: Path, modpackages_source: Path, sprite_scale_data: Dict[str, Tuple[int, int]], custom_scaling: Dict[str, float] = None, processed_pokemon_ids: Dict[str, set] = None, create_summary_table: bool = True, create_front_table: bool = True, create_back_table: bool = True):
        """Create scaling table files with custom values in temporary directory.
        
        Args:
            temp_dir: Temporary directory for creating files
            modpackages_source: Source directory for modpackages
            sprite_scale_data: Dictionary of sprite canvas sizes
            custom_scaling: Custom scaling configuration
            processed_pokemon_ids: Dictionary with 'front', 'back', and 'all' sets of Pokemon IDs
            create_summary_table: Whether to populate summary table with Pokemon IDs
            create_front_table: Whether to populate front table with Pokemon IDs
            create_back_table: Whether to populate back table with Pokemon IDs
        """
        try:
            # Set default scaling values (use custom values if provided, otherwise defaults)
            if custom_scaling:
                DEFAULT_SUMMARY_SCALE = custom_scaling.get('summary_scale', 2.7)
                DEFAULT_FRONT_SCALE = custom_scaling.get('front_scale', 1.0)
                DEFAULT_BACK_SCALE = custom_scaling.get('back_scale', 1.0)
                OVERRIDES = custom_scaling.get('overrides', {})
                
                self.logger.info(f"🎛️ Using default scaling: Summary({DEFAULT_SUMMARY_SCALE}), Front({DEFAULT_FRONT_SCALE}), Back({DEFAULT_BACK_SCALE})")
                
                # Count total overrides across all types
                total_overrides = 0
                if OVERRIDES:
                    total_overrides = len(OVERRIDES.get('summary', {})) + len(OVERRIDES.get('front', {})) + len(OVERRIDES.get('back', {}))
                
                self.logger.info(f"🎯 Custom overrides: {total_overrides} total (Summary: {len(OVERRIDES.get('summary', {}))}, Front: {len(OVERRIDES.get('front', {}))}, Back: {len(OVERRIDES.get('back', {}))})")
            else:
                DEFAULT_SUMMARY_SCALE = 2.7
                DEFAULT_FRONT_SCALE = 1.0
                DEFAULT_BACK_SCALE = 1.0
                OVERRIDES = {}
            
            # Create scaling table files with appropriate Pokemon IDs
            # Summary and Front tables use front sprite IDs, Back table uses back sprite IDs
            # Checkboxes control which Pokemon IDs are included in each table
            summary_ids = processed_pokemon_ids.get('front', set()) if (processed_pokemon_ids and create_summary_table) else set()
            front_ids = processed_pokemon_ids.get('front', set()) if (processed_pokemon_ids and create_front_table) else set()
            back_ids = processed_pokemon_ids.get('back', set()) if (processed_pokemon_ids and create_back_table) else set()
            
            # Always create all 3 tables, but content depends on checkbox flags
            scaling_tables = [
                ("table-summary-scale.txt", DEFAULT_SUMMARY_SCALE, OVERRIDES.get('summary', {}), summary_ids),
                ("table-front-scale.txt", DEFAULT_FRONT_SCALE, OVERRIDES.get('front', {}), front_ids),
                ("table-back-scale.txt", DEFAULT_BACK_SCALE, OVERRIDES.get('back', {}), back_ids)
            ]
            
            self.logger.info(f"📝 Creating scale tables (Summary: {create_summary_table}, Front: {create_front_table}, Back: {create_back_table})")
            
            for filename, default_scale, overrides, pokemon_ids in scaling_tables:
                table_path = temp_dir / filename
                self._create_single_scaling_table(table_path, default_scale, overrides, filename.replace('.txt', ''), modpackages_source, pokemon_ids)
                
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create scaling files with custom values: {e}")
    
    def _create_single_scaling_table(self, table_path: Path, default_scale: float, overrides: Dict[str, float], table_type: str, modpackages_source: Path, processed_pokemon_ids: set = None):
        """Create a single scaling table file with custom values.
        
        Args:
            table_path: Path where the table file will be created
            default_scale: Default scale value to use
            overrides: Dictionary of Pokemon ID -> scale overrides
            table_type: Type of table (for logging)
            modpackages_source: Path to modpackages source directory
            processed_pokemon_ids: Set of Pokemon IDs that were actually processed (have replacement sprites)
        """
        try:
            header_lines = []
            
            # Try to get original headers from modpackages
            original_table_path = modpackages_source / "sprites" / "battlesprites" / table_path.name
            if original_table_path.exists():
                with open(original_table_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not '=' in line:
                            # This is a header line (comment or empty line)
                            header_lines.append(line)
                        elif '=' in line:
                            # We've reached the data section, stop reading headers
                            break
            
            # If no headers found, use default headers
            if not header_lines:
                header_lines = [
                    ";Table which determines scales for battle sprites.",
                    ";Lines starting with ; will be ignored",
                    ";Please only include values for overriden sprites!",
                    ";Each entry should be a separate line and contain ID=SCALE, like \"1=3\" without quotes."
                ]
            
            # Generate entries only for processed Pokemon or those with overrides
            final_entries = {}
            
            # Add entries for Pokemon with overrides (these always get added)
            for dex_str, scale in overrides.items():
                final_entries[dex_str] = scale
            
            # Add entries for processed Pokemon (only if not already in overrides)
            if processed_pokemon_ids:
                for dex_str in processed_pokemon_ids:
                    if dex_str not in final_entries:
                        # Use default scale for processed Pokemon without overrides
                        final_entries[dex_str] = default_scale
            
            # Write the scaling table file
            with open(table_path, 'w', encoding='utf-8') as f:
                # Write header lines
                for line in header_lines:
                    f.write(line + '\n')
                
                # Write updated entries, sorted by dex number
                for dex_id in sorted(final_entries.keys(), key=int):
                    f.write(f"{dex_id}={final_entries[dex_id]:.2f}\n")
            
            override_count = len([d for d in final_entries.keys() if d in overrides])
            self.logger.info(f"📊 Created {table_type} scale table at {table_path} with {len(final_entries)} entries (default: {default_scale:.2f}, overrides: {override_count})")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create {table_type} scale table: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
    
    def _create_mod_metadata(self, mod_dir: Path, mod_name: str, mod_version: str, 
                           mod_author: str, mod_description: str, target_game: str):
        """Create mod metadata files."""
        
        # Create info.xml (matching the extracted mod format exactly)
        info_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<resource name="{mod_name}" version="{mod_version}" description="{mod_description}" author="{mod_author}" 
          weblink="https://forums.pokemmo.com/index.php?/topic/192232-bullseye-injector-a-complete-understanding-of-your-enemies-10/">
</resource>'''
        
        info_file = mod_dir / "info.xml"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(info_xml)
        
        # Get sprite count for README
        gif_count = len(list((mod_dir / "sprites" / "battlesprites").glob("*.gif")))
        png_count = len(list((mod_dir / "sprites" / "battlesprites").glob("*.png")))
        sprite_count = gif_count + png_count
        
        # Create README.md with mod.json content integrated
        readme_content = f"""# {mod_name}

**Version:** {mod_version}  
**Author:** {mod_author}  
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Created by:** Bullseye Injector

## Description
{mod_description}

## Mod Information
- **Name:** {mod_name}
- **Version:** {mod_version}
- **Author:** {mod_author}
- **Description:** {mod_description}
- **Target Game:** {target_game}
- **Created Date:** {datetime.now().isoformat()}
- **Created By:** Bullseye Injector
- **Sprite Count:** {sprite_count}
- **Compatibility:** Latest game version, Universal platform
- **Installation Type:** Sprite replacement

## Installation Instructions
1. Extract the mod files to your game's sprite directory
2. Backup your original sprites before installation
3. Replace existing sprite files with the modded versions
4. Launch the game to see the changes

## Contents
- **Sprite Count:** {sprite_count} sprites
- **Target Game:** {target_game}
- **Format:** GIF and PNG sprites with transparency support

## Compatibility
- **Game Version:** Latest
- **Platform:** Universal
- **Sprite Format:** Animated GIF and PNG with alpha channel

## Support
This mod was created using the Bullseye Injector tool.
For support or updates, please refer to the original tool documentation.

## Changelog
### Version {mod_version}
- Initial release
- Generated using Bullseye Injector
- All sprites processed and optimized
"""
        
        readme_file = mod_dir / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.logger.info("📄 Created mod metadata and documentation")
    
    def _sanitize_mod_name(self, name: str) -> str:
        """
        Sanitize mod name for safe use in file systems and XML.
        
        Args:
            name: Raw mod name input
            
        Returns:
            Sanitized mod name safe for file systems and XML
        """
        if not name:
            return ""
        
        # Remove or replace invalid characters for file systems
        # Windows/Linux/Mac invalid characters: < > : " / \ | ? *
        sanitized = re.sub(r'[<>:"/\\|?*]', '', name)
        
        # Remove control characters (ASCII 0-31)
        sanitized = re.sub(r'[\x00-\x1f]', '', sanitized)
        
        # Remove leading/trailing spaces and dots (Windows restriction)
        sanitized = sanitized.strip('. ')
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Limit length to avoid path issues (Windows has 260 char path limit)
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        return sanitized.strip()
    
    def _sanitize_mod_description(self, description: str) -> str:
        """
        Sanitize mod description for safe use in XML.
        
        Args:
            description: Raw mod description input
            
        Returns:
            Sanitized description safe for XML
        """
        if not description:
            return ""
        
        # Remove or replace XML special characters
        # & < > " ' are XML entities that need escaping
        sanitized = description
        
        # Escape XML entities
        sanitized = sanitized.replace('&', '&amp;')
        sanitized = sanitized.replace('<', '&lt;')
        sanitized = sanitized.replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;')
        sanitized = sanitized.replace("'", '&apos;')
        
        # Remove control characters (ASCII 0-31) except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', sanitized)
        
        # Replace multiple whitespace with single space, preserve line breaks
        sanitized = re.sub(r'[ \t]+', ' ', sanitized)
        sanitized = re.sub(r'\n\s*\n', '\n\n', sanitized)  # Preserve paragraph breaks
        
        # Limit length to reasonable size
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000] + "..."
        
        return sanitized.strip()
    
    def _package_mod(self, mod_dir: Path, mod_name: str, use_mod_zip_extension: bool = False) -> Path:
        """Package the mod directory into the final mod file."""
        
        # Get all files to be packaged
        all_files = list(mod_dir.rglob("*"))
        file_count = len([f for f in all_files if f.is_file()])
        
        # For .mod files, use the existing Template.zip as base and add sprite files
        # Sanitize mod name for filename to avoid Windows issues
        safe_mod_filename = re.sub(r'[<>:"/\\|?*]', '', mod_name)
        
        # Determine final extension based on user preference
        final_extension = ".mod.zip" if use_mod_zip_extension else ".mod"
        mod_file = mod_dir.parent / f"{safe_mod_filename}{final_extension}"
            
        # Find the Template.zip file - handle both development and packaged executable modes
        def get_template_zip_path():
            searched_paths = []
                
            # Check if running as PyInstaller executable
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                self.logger.info("🔍 Running as packaged executable, searching for Template.zip...")
                    
                # Running as packaged executable - look in the temporary extraction directory
                template_path = Path(sys._MEIPASS) / "Template.zip"
                searched_paths.append(str(template_path))
                self.logger.info(f"🔍 Checking PyInstaller temp dir: {template_path}")
                if template_path.exists():
                    return template_path
                    
                # Also check in the executable's directory
                exe_dir = Path(sys.executable).parent
                template_path = exe_dir / "Template.zip"
                searched_paths.append(str(template_path))
                self.logger.info(f"🔍 Checking executable dir: {template_path}")
                if template_path.exists():
                    return template_path
            else:
                self.logger.info("🔍 Running as script, searching for Template.zip...")
                    
                # Running as script - look in the project root
                template_path = Path(__file__).parent / "Template.zip"
                searched_paths.append(str(template_path))
                self.logger.info(f"🔍 Checking script dir: {template_path}")
                if template_path.exists():
                    return template_path
                
            # If not found in expected locations, search more broadly
            additional_paths = [
                Path.cwd() / "Template.zip",  # Current working directory
                Path(__file__).parent.parent / "Template.zip",  # Parent of script directory
            ]
                
            for path in additional_paths:
                searched_paths.append(str(path))
                self.logger.info(f"🔍 Checking additional path: {path}")
                if path.exists():
                    return path
                
            # Log all searched paths for debugging
            self.logger.error(f"❌ Template.zip not found in any of these locations:")
            for path in searched_paths:
                self.logger.error(f"   - {path}")
                
            return None
            
        template_zip_path = get_template_zip_path()
            
        if not template_zip_path:
            raise FileNotFoundError(f"Template.zip not found. Check logs above for all searched locations.")
            
        self.logger.info(f"📦 Sprite files to add: {len([f for f in all_files if f.suffix.lower() in ['.gif', '.png']])}")
            
        # Clone Template.zip and append all files from working directory
        try:
            # Copy the template to a temporary zip file
            # Use .tmp.zip suffix to avoid conflicts with final .mod.zip extension
            temp_final_zip = mod_dir.parent / f"{safe_mod_filename}.tmp.zip"
            shutil.copy2(template_zip_path, temp_final_zip)
            self.logger.info(f"📦 Cloned template to: {temp_final_zip}")
            
            # Ensure the file is fully written and closed before proceeding
            time.sleep(0.1)
                
            # Append all files from the working directory to the cloned template
            with zipfile.ZipFile(temp_final_zip, 'a', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
                def natural_key(p: Path):
                    s = str(p).replace("\\", "/")

                    # Folders first by depth, then numerically by name
                    parts = re.split(r'(\d+)', s)
                    return (s.count("/"), [int(t) if t.isdigit() else t.lower() for t in parts])

                for file_path in sorted([Path(f) for f in all_files if Path(f).is_file()], key=natural_key):
                    # Create a relative path to use as the archive name
                    arcname = os.path.relpath(file_path, mod_dir)
                            
                    def add_file_with_dirs(zf, file_path, arcname):
                        # Create directory entries for all parents
                        parent = Path(arcname).parent
                        parts = []
                        while parent != Path("."):
                            parts.append(str(parent).replace("\\", "/") + "/")
                            parent = parent.parent
                        for folder in reversed(parts):
                            folder = folder.replace("\\", "/")
                            if folder not in zf.namelist():
                                zf.writestr(folder, b"")  # Explicit empty folder entry (for WinRAR-style)

                        zf.write(file_path, arcname)

                    add_file_with_dirs(zf, file_path, arcname)

                    # Log important files with their directory structure
                    if file_path.name.lower().endswith(('.gif', '.png')):
                        self.logger.info(f"📦 Added sprite: {arcname}")
                    elif file_path.name in ['info.xml', 'README.md']:
                        self.logger.info(f"📦 Added metadata: {arcname}")
                    elif 'sprites' in arcname:
                        self.logger.info(f"📦 Added sprite file: {arcname}")
                    elif 'table' in arcname:
                        self.logger.info(f"📦 Added scaling table: {arcname}")
                
            # Test the created archive for corruption
            with zipfile.ZipFile(temp_final_zip, 'r') as test_zf:
                test_result = test_zf.testzip()
                if test_result:
                    self.logger.warning(f"⚠️ Archive corruption detected in: {test_result}")
                else:
                    self.logger.info("✅ No corruption detected in ZIP archive")
                
            # Validate the created file is a valid zip
            if zipfile.is_zipfile(temp_final_zip):
                self.logger.info("✅ Final zip file is a valid ZIP archive")
            else:
                self.logger.error("❌ Final zip file is not a valid ZIP archive")
                
            # Ensure the zip file is properly closed before renaming
            # The 'with' statement should have already closed it, but let's be explicit
            time.sleep(0.1)  # Small delay to ensure file handles are released
                
            # Now rename the zip file to final extension
            try:
                shutil.move(str(temp_final_zip), str(mod_file))
                self.logger.info(f"📦 Created mod file: {mod_file}")
            except PermissionError as pe:
                self.logger.error(f"❌ Permission error renaming file: {pe}")
                # Try to delete the target file if it exists and try again
                if mod_file.is_file():
                    mod_file.unlink()
                    shutil.move(str(temp_final_zip), str(mod_file))
                    self.logger.info(f"📦 Created mod file (after cleanup): {mod_file}")
                else:
                    raise
            
        except Exception as e:
            self.logger.error(f"❌ Failed to append files to cloned template: {e}")

            # Fallback: try a different approach - create a new zip with all files
            self.logger.info("📦 Attempting fallback: creating empty mod")
            try:
                # Copy the template to a temporary zip file (not .mod yet)
                if not temp_final_zip.exists():
                    temp_final_zip = mod_file.with_suffix('.zip')

                shutil.copy2(template_zip_path, temp_final_zip)
                self.logger.info(f"📦 Cloned template to: {temp_final_zip}")
            
                # Ensure the file is fully written and closed before proceeding
                time.sleep(0.1)
                
                # Rename the fallback zip to .mod
                shutil.move(str(temp_final_zip), str(mod_file))
                self.logger.error(f"📦 Fallback: created empty mod: {mod_file}")

            except Exception as fallback_error:
                self.logger.error(f"❌ Fallback also failed: {fallback_error}")
        
        return mod_file