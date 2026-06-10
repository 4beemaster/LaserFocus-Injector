# LaserFocus Injector - Complete Feature Summary

## Overview

Major refactoring and feature additions to the LaserFocus Injector sprite processing system, including badge system overhaul, performance optimizations, advanced sprite handling, and code maintainability improvements.

---

## 1. Badge System Refactor

### Changed From → To

- **Old**: Extracted badges from Bullseye sprites via component analysis
- **New**: Direct loading from `badges/` folder using Pokemon weakness data

### Key Features

- Folder-based badge loading from `badges/` directory
- Badge scaling: 1/8th of max sprite height (separate for front/back)
- Automatic shiny badge detection and placement (top of stack)
- Badge ordering: Shiny → 4x weaknesses → 2x weaknesses
- Uses `pokemon_weaknesses.json` for weakness lookup

---

## 2. Performance Optimization

### Two-Pass Processing System

- **Pass 1**: Fast image header scanning (img.height only) to determine max heights
  - No pixel decoding for better performance
  - Separate max heights for front/back sprites
- **Pass 2**: Process sprites with calculated badge heights

### Performance Results

- 2,882 sprites scanned in 1.48 seconds
- ~1,945 files/second scan rate

---

## 3. Back Sprite Control

### "Add badges to back sprites" Checkbox

- **Default**: OFF - Back sprites bulk copied without badge processing
- **Enabled**: Back sprites processed with badges like front sprites
- Improves processing speed when badges not needed on back sprites

---

## 4. Original Sprites Fallback System

### Required Fallback Coverage

- Bullseye sprites directory now **required** (not optional)
- All Bullseye sprites batch copied to output first
- Replacement sprites then overwrite Bullseye originals
- Ensures complete Pokemon coverage even with partial custom sprite sets

---

## 5. Smart Sprite Limiting

### Limit by Unique Pokemon ID

- Counts unique Pokemon (not total files)
- **Conditional back sprite handling**:
  - When processing back sprites with badges: Limit applies to both front & back
  - When NOT processing back sprites: Limit applies to front only, all back sprites included

### Example

- Limit = 10, Back badges OFF: 10 front sprites + all matching back sprites
- Limit = 10, Back badges ON: 10 Pokemon total (both front and back)

---

## 6. Minimum Height & Padding

### Front Sprite Minimum Height

- Minimum height: 51% of max front sprite height
- Ensures consistent vertical space for all front sprites
- **Note**: Only works properly if sprites already fit correctly in-game. If original sprites are misaligned, this could cause them to appear too high or too low on screen.

### Smart Padding System

- **Top Padding**: When sprite canvas < minimum height (brings to baseline)
- **Bottom Padding**: When badges extend beyond sprite height (centers sprite)
- Never applies both paddings simultaneously
- Back sprites: Only bottom padding for badge overhang

---

## 7. Shiny Hunter Mode

### Two Operational Modes

**Mode 1: Bullseye normals + Replacement shinies (`bullseye_normal`)**

- Only processes shiny front sprites from replacement set
- All back sprites processed normally
- Normal front sprites use original Bullseye mod sprites
- **Scale Tables**: Shiny front sprites excluded from scaling (use Bullseye originals), back sprites included
- **Use Case**: When you only want custom shiny front sprites, keeping Bullseye normals intact

**Mode 2: Replacement normals + Bullseye shinies (`replacement_normal`)**

- Only processes normal front sprites from replacement set
- All back sprites processed normally
- Shiny front sprites use original Bullseye mod sprites
- **Scale Tables**: Normal front sprites included in scaling, shiny front sprites excluded
- **Use Case**: When you only want custom normal front sprites, keeping Bullseye shinies intact

### Implementation Details

- Filter applied AFTER height scanning to preserve accurate badge sizing
- Excluded sprites still processed but not added to results or scale tables
- Back sprites always processed regardless of mode (all variants included)
- Maintains complete coverage by using Bullseye sprites for excluded variants

---

## 8. Scale Table Control System

### Three Independent Checkboxes

- **Create Summary Table**: Controls if summary scale table is populated with Pokemon IDs
- **Create Front Table**: Controls if front scale table is populated with Pokemon IDs
- **Create Back Table**: Controls if back scale table is populated with Pokemon IDs

### Behavior

- **All tables always created** (even if checkboxes unchecked) to maintain mod structure
- Unchecked boxes result in header-only tables (no Pokemon entries)
- Checked boxes populate tables with Pokemon IDs from processed replacement sprites
- Custom scale overrides always included regardless of checkbox state
- Default values: All three checkboxes enabled

### Use Cases

- Disable summary/front tables in Shiny Hunter mode when normals use Bullseye originals
- Disable specific tables when only certain sprite types need custom scaling
- Keep back table enabled when front sprites don't need scaling adjustments

---

## 9. Scale Table Optimization

### Only Replacement Sprites in Tables

- `table-front-scale.txt`, `table-back-scale.txt`, `table-summary-scale.txt`
- **Changed**: Only includes replacement sprites (not all 1-1024 Pokemon)
- Tracks sprites that were:
  - Processed with badges
  - Bulk-copied as replacements
  - Have custom scale overrides
- Bullseye originals without replacements: Not included

### Special Handling

- **Shiny Hunter Mode**: Excluded sprites (e.g., shinies in `bullseye_normal` mode) not added to scale tables
- **Empty sprite_scale_data**: Tables still created to maintain mod structure (may be empty in Shiny Hunter mode)
- **Checkbox Control**: Table population controlled by Create Summary/Front/Back Table checkboxes
- **Always Created**: All three table files always created, content depends on flags

---

## 10. Custom Scaling Configuration

### Default Scale Values

- **Summary Scale**: Default scale for Pokemon summary screens (default: 2.7)
- **Front Scale**: Default scale for front-facing sprites (default: 1.0)
- **Back Scale**: Default scale for back-facing sprites (default: 1.0)

### Individual Pokemon Overrides

- Override specific Pokemon with custom scale values
- Organized by table type: summary, front, back
- Format: `{"001": 3.0, "025": 2.5}` (Pokemon ID → scale value)
- Overrides take precedence over default values
- Supports Pokemon #001-1024

### Configuration Sources

- **GUI**: Scale configuration dialog with default values and override controls
- **Settings File**: Persisted in `sprite_converter_settings.json`
- **Mod Creation**: Applied during mod packaging to scale table files

---

## 11. Code Refactoring & Maintainability

### Shared Helper Functions (CLI & GUI)

Created 8 shared functions to eliminate ~200+ lines of duplicate code:

1. `apply_sprite_limit()` - Pokemon ID limiting with conditional back sprite handling
2. `scan_sprite_heights()` - Fast height scanning (header-only reads)
3. `calculate_badge_and_min_heights()` - Badge and minimum height calculations
4. `copy_bullseye_sprites_as_fallback()` - Batch copy Bullseye originals
5. `separate_front_back_sprites()` - Split sprite lists by type
6. `bulk_copy_back_sprites()` - Copy back sprites without badge processing
7. `determine_sprites_to_process()` - Decide which sprites get badges
8. `save_processing_summary()` - Save results to JSON summary

### Benefits

- Single source of truth for business logic
- Updates automatically propagate to both CLI and GUI
- Easier testing and maintenance
- Consistent behavior across interfaces

---

## Modified Files

### `sprite_processor.py`

- Complete badge system overhaul
- Two-pass processing implementation
- Added 8 shared helper functions
- Padding logic for sprite alignment
- Results tracking for all sprite types

### `sprite_converter_gui.py`

- "Add badges to back sprites" checkbox
- Shiny Hunter Mode with two operational modes
- Three scaling table control checkboxes
- Custom scaling configuration dialog
- Uses shared functions from sprite_processor
- Updated to support all new features
- Improved logging and progress reporting

### `mod_packager.py`

- Accepts `replacement_sprite_names` parameter for tracking processed sprites
- Only includes replacement sprites in scale tables (not Bullseye originals)
- Handles empty `sprite_scale_data` (e.g., in Shiny Hunter mode)
- Always creates all three scale table files regardless of content
- Checkbox control for table population (create_summary_table, create_front_table, create_back_table)
- Custom scaling configuration support (default values and individual overrides)
- Override values take precedence over defaults

### `LaserFocusInjector.spec`

- Added `sprite_processor` to hidden imports
- Ensures shared functions work in compiled EXE

---

## File Requirements

### Required Files & Directories

1. **`badges/`** - Badge PNG images (37 files)
   - Type badges: `Fire.png`, `Water.png`, etc.
   - 4x badges: `Fire-4.png`, `Water-4.png`, etc.
   - `Shiny.png` for shiny variants

2. **`pokemon_weaknesses.json`** - Pokemon weakness data

3. **Bullseye sprites directory** - Complete original sprite set (required fallback)

4. **Replacement sprites** - Custom sprites to process with badges

### Naming Convention

`<id>-<front|back>-<variant>[-s][-m|-f].gif`

Examples:

- `001-front-n.gif` - Bulbasaur front normal
- `025-back-s.gif` - Pikachu back shiny
- `150-front-s-m.gif` - Mewtwo front shiny male

---

## Usage

### GUI

1. Select Bullseye sprites directory (required)
2. Select replacement sprites directory
3. Toggle "Add badges to back sprites" (optional)
4. Set limit (optional)
5. Enable Shiny Hunter Mode (optional):
   - Mode 1: Bullseye normals + Replacement shinies
   - Mode 2: Replacement normals + Bullseye shinies
6. Click Start
7. Configure mod settings in dialog:
   - Set mod name, version, authors, description
   - Configure scaling table creation (optional):
     - Create Summary Table (default: checked)
     - Create Front Table (default: checked)
     - Create Back Table (default: checked)
   - Configure custom scaling (optional):
     - Default scale values for summary/front/back
     - Individual Pokemon overrides
8. Click Build Mod

### CLI

```bash
python sprite_processor.py \
  --sprite-dir "path/to/custom/sprites" \
  --output-dir "path/to/output" \
  --badges-dir "badges" \
  --weaknesses-json "pokemon_weaknesses.json" \
  --bullseye-dir "path/to/bullseye/sprites" \
  --limit 50 \
  --process-back-sprites \
  --shiny-hunter-mode bullseye_normal
```

**Shiny Hunter Mode Options:**

- `bullseye_normal`: Bullseye normals + Replacement shinies
- `replacement_normal`: Replacement normals + Bullseye shinies
- Omit parameter for standard processing (all sprites)

---

## Benefits Summary

1. ✅ **Better Performance**: Fast two-pass scanning (~2000 files/sec)
2. ✅ **Flexible Processing**: Optional back sprite badge processing
3. ✅ **Complete Coverage**: Bullseye fallback ensures no missing sprites
4. ✅ **Smart Limiting**: Pokemon ID-based limiting with conditional logic
5. ✅ **Consistent Sizing**: Minimum heights and smart padding
6. ✅ **Optimized Output**: Scale tables only for replacement sprites
7. ✅ **Maintainable Code**: ~200 lines of duplication eliminated
8. ✅ **Better Quality**: Direct PNG badges vs. extracted GIF badges
9. ✅ **Easy Updates**: Badges can be changed without code modifications
10. ✅ **Automatic Shiny**: Built-in shiny detection and badge placement
11. ✅ **Shiny Hunter Mode**: Two modes for mixing custom and Bullseye sprites
12. ✅ **Scale Table Control**: Independent control over which tables are populated
13. ✅ **Custom Scaling**: Default values and individual Pokemon overrides
14. ✅ **Robust Packaging**: Handles edge cases like empty sprite data gracefully
