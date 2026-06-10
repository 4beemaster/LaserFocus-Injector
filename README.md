# 🎯 LaserFocus Injector

A powerful sprite mod creation tool for PokeMMO that automatically adds type weakness badges to your custom sprites.

## ❓ What is LaserFocus Injector?

**LaserFocus Injector** automates the creation of PokeMMO sprite mods with type weakness badges. Instead of manually editing hundreds of sprites, it takes your custom sprites and automatically adds professionally-designed type weakness badges to them, then packages everything into a ready-to-install mod file.

### What It Does

1. **Takes Your Custom Sprites**: Provide your custom Pokemon sprites (front and back views)
2. **Adds Type Weakness Badges**: Automatically adds badges showing type weaknesses (Fire, Water, etc.) based on each Pokemon's type matchups
3. **Uses Original Sprites as Fallback**: Includes original Bullseye mod sprites for any Pokemon you don't provide custom sprites for
4. **Creates Complete Mod**: Packages everything into a single .mod file ready for PokeMMO

### Key Features

- **Automatic Badge Addition**: Adds type weakness badges (2x and 4x weaknesses, plus shiny indicators) to all sprites
- **Smart Badge Placement**: Badges are automatically sized and positioned at the bottom of each sprite
- **Complete Coverage**: Uses original Bullseye sprites as fallback so every Pokemon has a sprite
- **Batch Processing**: Process hundreds of sprites at once
- **Professional Output**: Creates ready-to-install PokeMMO .mod files

## ✨ Features

### Core Functionality

- **Automatic Badge Addition**: Adds type weakness badges to your custom sprites automatically
- **Badge Folder System**: Loads badges directly from PNG files in the badges/ folder (no extraction needed)
- **Original Sprite Fallback**: Uses Bullseye mod sprites for Pokemon you don't provide custom sprites for
- **Professional Mod Packaging**: Creates complete PokeMMO-compatible .mod files with one click
- **Batch Processing**: Process entire sprite collections at once (hundreds of sprites)

### Advanced Features

- **Smart Badge Sizing**: Badges automatically scale to 1/8th of sprite height (separate for front/back)
- **Minimum Height Control**: Ensures consistent sprite heights with smart padding (51% of max height)
- **Badge Processing Control**: Optional checkbox to add badges to back sprites (off by default for performance)
- **Shiny Hunter Mode**: Two modes for mixing custom and original Bullseye sprites
  - Mode 1: Bullseye normals + Replacement shinies (only custom shiny fronts get badges)
  - Mode 2: Replacement normals + Bullseye shinies (only custom normal fronts get badges)
- **Scaling Table Control**: Independent checkboxes to control which scale tables are populated
- **Gender Variant Support**: Automatic detection and processing of male/female sprite variants
- **Shiny Badge Detection**: Automatically places shiny badges on top of type weakness badges
- **Quality Preservation**: No quality loss - sprites processed with proper canvas expansion
- **Animation Preservation**: Maintains GIF timing, disposal methods, and loop information
- **Real-time Preview**: See processed sprites before final output
- **Comprehensive Validation**: Multi-pass analysis for file compatibility and missing variants
- **Memory Optimization**: LRU caching system for efficient preview handling
- **Cross-Platform**: Works on Windows, Linux, and macOS

### Scaling Configuration

- **Default Scaling Values**: Set base scaling for summary, front, and back sprites
- **Individual Overrides**: Override scaling for specific Pokemon with precision controls
- **Real-time Configuration**: Changes save automatically and persist across sessions
- **Pokemon Detection**: Only shows Pokemon that exist in your sprite collection
- **Range Support**: Handles Pokemon #001-1024 with dynamic detection

## 🚀 Quick Start

### Installation

1. Download the latest release or build from source
2. Extract to your desired location
3. Run `LaserFocusInjector.exe` (Windows) or `python sprite_converter_gui.py` (source)

### Basic Usage

1. **Set Directories**:
   - **Bullseye Sprites**: Path to original Bullseye mod sprites (required - used as fallback)
   - **Replacement Sprites**: Path to your custom sprites (sprites you want badges added to)
   - **Output Directory**: Where to save the processed sprites and final mod

2. **Configure Settings**:
   - **Process All**: Process entire sprite collection
   - **Limit**: Process only specific Pokemon (e.g., limit to first 50 Pokemon)
   - **Add badges to back sprites**: Check to process back sprites with badges (unchecked = faster, bulk copy only)
   - **Shiny Hunter Mode**: Optional modes for mixing custom and Bullseye sprites
     - Mode 1: Bullseye normals + Replacement shinies (only custom shiny front sprites get badges)
     - Mode 2: Replacement normals + Bullseye shinies (only custom normal front sprites get badges)
   - **Show Logs**: Display detailed processing information

3. **Build Your Mod**:
   - Click **"Start"** to open the mod configuration dialog
   - Set mod name, version, authors, and description
   - Configure sprite scaling if needed (optional):
     - Set default scale values for summary, front, and back sprites
     - Add individual Pokemon overrides for custom scaling
   - Control which scale tables are populated (optional):
     - Create Summary Table (default: checked)
     - Create Front Table (default: checked)
     - Create Back Table (default: checked)
   - Click **"Build Mod"** to create your .mod file

## 📁 Directory Structure

### Required Files

```text
Your Project/
├── LaserFocusInjector.exe          # Main application
├── Template.zip                    # Mod packaging template
├── Bullseye Sprites/               # Original Bullseye mod sprites (fallback)
│   └── sprites/battlesprites/
│       ├── 001-front-n.gif
│       ├── 001-back-n.gif
│       └── ...
└── Custom Sprites/                 # Your custom replacement sprites
    ├── 001-front-n.gif
    ├── 001-back-n.gif
    └── ...
```

### Output Structure

```text
Output/
├── 001-front-n.gif              # Processed sprites
├── 001-back-n.gif
├── table-front-scale.txt           # Scale configuration (only replacement sprites)
├── table-back-scale.txt
├── table-summary-scale.txt
├── YourModName.mod                 # Final mod file
└── logs/
    └── process.log                 # Detailed processing log
```

## 🎮 Sprite Scaling System

### How It Works

The scaling system controls how sprites appear in-game:

- **Summary Scale**: Controls sprite size in Pokemon summary screens
- **Front Scale**: Controls sprite size when facing forwards (opponent's Pokemon)
- **Back Scale**: Controls sprite size when facing backwards (your Pokemon)

**Note**: Scale tables only include sprites you provide (replacement sprites), not the original Bullseye sprites used as fallback.

### Table Population Control

Three independent checkboxes control which scale tables are populated:

- **Create Summary Table**: Populates summary scale table with Pokemon IDs (default: checked)
- **Create Front Table**: Populates front scale table with Pokemon IDs (default: checked)
- **Create Back Table**: Populates back scale table with Pokemon IDs (default: checked)

**Important**: All three table files are always created to maintain mod structure. Unchecked boxes result in header-only tables (no Pokemon entries), which means those sprites will use game defaults. This is useful in Shiny Hunter Mode when certain sprite types use Bullseye originals.

### Configuration Options

- **Default Values**: Set base scaling for all Pokemon
- **Individual Overrides**: Override specific Pokemon with custom values
- **Range**: 0.0 to 10.0 (recommended: 1.0-3.0)

### Shiny Hunter Mode Behavior

When using Shiny Hunter Mode:

- **Mode 1 (Bullseye normals + Replacement shinies)**:
  - Custom shiny front sprites are excluded from scale tables
  - Normal front sprites use Bullseye originals (Shiny replacements use game default scale)
  - Back sprites included in back scale table
  - Consider unchecking "Create Summary Table" and "Create Front Table" since normals use Bullseye sprites

- **Mode 2 (Replacement normals + Bullseye shinies)**:
  - Custom normal front sprites included in scale tables
  - Shiny front sprites use Bullseye originals (Bullseye shinies use custom scale)
  - Back sprites included in back scale table

### Example Usage

- **Default Summary Scale**: 2.7 (good for most sprites)
- **Default Front Scale**: 1.0 (standard size)
- **Default Back Scale**: 1.0 (standard size)
- **Override Pokemon #150**: Set to 0.8 for smaller appearance

## 🔍 Analysis & Validation Features

### Comprehensive File Analysis

- **Multi-Level Matching**: Direct matches, case-insensitive, normalized, and cross-type matching
- **Gender Variant Detection**: Automatically identifies male/female sprite variants (-m/-f suffixes)
- **Missing File Analysis**: Identifies missing sprites with source file suggestions
- **Duplicate Detection**: Prevents conflicts using signature-based duplicate identification
- **Malformed File Correction**: Fixes common issues like double extensions (.gif.gif → .gif)

### Validation Engine

- **Phase 1**: Simple fixes (case corrections, extension fixes, malformed files)
- **Phase 2**: Missing file analysis with intelligent source identification
- **Phase 2.5**: Back file detection for all front files
- **Phase 3**: Cleanup of unnecessary files and optimization
- **Deduplication**: Signature-based duplicate detection with conflict prevention

### Smart Recommendations

- **File Operations**: rename, clone, create_gender_variant, create_base_from_male/female, remove_base, cleanup
- **Priority System**: Organized operation priority to prevent conflicts
- **Retry Mechanism**: 3 attempts for permission errors with 1-second delays
- **Conflict Resolution**: Intelligent handling of duplicate files and naming conflicts

## 🆚 Feature Comparison

| Feature                    | Traditional Manual Editing | LaserFocus Injector               |
| -------------------------- | -------------------------- | --------------------------------- |
| **Badge Preservation**     | ❌ Manual recreation       | ✅ Automatic preservation         |
| **Quality Loss**           | ❌ Often occurs            | ✅ Canvas expansion prevents loss |
| **Gender Variants**        | ❌ Manual handling         | ✅ Automatic detection            |
| **Batch Processing**       | ❌ One at a time           | ✅ Entire collections             |
| **Mod Creation**           | ❌ Manual packaging        | ✅ One-click generation           |
| **Time Investment**        | ❌ Hours per sprite        | ✅ Minutes per collection         |

## 🏗️ Technical Overview

### Core Components

- **Badge Loading System**: Direct PNG loading from badges/ folder using pokemon_weaknesses.json
- **Two-Pass Processing**: Fast image header scanning (~1,945 files/sec) followed by badge processing
- **Shiny Hunter Mode**: Two operational modes for mixing custom and Bullseye sprites
- **Image Processing Engine**: Adds badges using PIL/Pillow with smart sizing and positioning
- **GUI Framework**: Modern dark-themed interface with real-time preview and threaded processing
- **Mod Packaging System**: Creates professional PokeMMO-compatible mod files with proper metadata
- **Scaling System**: Advanced configuration with default values, individual Pokemon overrides, and table control

### Processing Capabilities

- **Badge Composition**: Automatically adds type weakness badges to bottom of sprites
- **Badge Scaling**: 1/8th of max sprite height (separate calculations for front/back sprites)
- **Badge Ordering**: Shiny badge (if applicable) → 4x weakness badges → 2x weakness badges
- **Minimum Height**: Front sprites padded to 51% of max height for consistency
- **Smart Padding**: Top padding OR bottom padding based on sprite and badge dimensions
- **Animation Handling**: Maintains GIF timing, disposal methods, and loop information
- **Batch Processing**: Handles entire sprite collections (1000+ files) efficiently
- **Memory Management**: LRU caching system with automatic cleanup
- **Fallback System**: Automatically copies original Bullseye sprites for complete coverage

### Supported Formats

- **Input**: GIF and PNG files with full transparency support
- **Output**: Optimized GIF files with complete animation preservation
- **Mod Format**: Standard PokeMMO .mod files with proper structure
- **Configuration**: JSON-based settings with persistent storage

### File Naming Convention

Standard format: `XXX-direction-variant-gender.ext`

- **XXX**: Three-digit Pokemon number (001-1024)
- **direction**: front, back
- **variant**: n (normal), s (shiny)
- **gender**: m (male), f (female), or omitted for no gender difference
- **ext**: gif or png

Examples:

- `001-front-n.gif` - Bulbasaur front normal
- `025-back-s.gif` - Pikachu back shiny  
- `150-front-s-m.gif` - Mewtwo front shiny male

## 🔧 Configuration

### Settings File (`sprite_converter_settings.json`)

The app automatically saves your preferences:

```json
{
  "move_dir": "path/to/bullseye/sprites",
  "sprite_dir": "path/to/replacement/sprites", 
  "output_dir": "path/to/output",
  "log_dir": "logs",
  "use_custom_log_dir": false,
  "process_all": true,
  "show_logs": true,
  "limit": "",
  "shiny_hunter_mode": false,
  "shiny_mode_option": "bullseye_normal",
  "create_summary_table": true,
  "create_front_table": true,
  "create_back_table": true,
  "default_summary_scale": 2.7,
  "default_front_scale": 1.0,
  "default_back_scale": 1.0,
  "summary_overrides": {"001": 3.0, "025": 2.5},
  "front_overrides": {"150": 0.8, "151": 0.9},
  "back_overrides": {"150": 0.6, "151": 0.7}
}
```

### Build Configuration

- **Mod Name**: Custom name for your mod
- **Version**: Semantic versioning (e.g., "1.0")
- **Authors**: Auto-includes "UncleTyrone, Zoruah" + custom authors
- **Description**: Custom mod description

## 🖥️ User Interface Features

### Modern Dark Theme

- **Color Scheme**: Professional dark theme with purple accents (#8e44ad)
- **Responsive Design**: Adapts to different window sizes and screen resolutions
- **Hover Effects**: Interactive feedback for buttons and controls
- **High Contrast**: Excellent readability with sufficient contrast ratios

### Real-time Features

- **Live Preview**: Cycles through last 10 processed sprites (800ms per sprite)
- **Progress Tracking**: Animated progress bars during file analysis and processing
- **Log Integration**: Real-time log display with color-coded messages
- **Status Updates**: Live status updates during all operations

### Interactive Elements

- **Directory Browsing**: Easy folder selection with browse buttons
- **Drag & Drop**: Support for dragging folders into directory fields
- **Keyboard Navigation**: Full keyboard support for all operations
- **Tooltips**: Helpful descriptions for complex operations and settings

### Advanced UI Capabilities

- **Lazy Loading**: Issues tabs load content on-demand to prevent startup lag
- **Debounced Search**: Search operations are optimized to prevent excessive filtering
- **Memory-efficient Display**: Only loads first frame of GIFs for preview cycling
- **Error Handling**: Clear, actionable error messages with suggested solutions

## 🔧 Troubleshooting

### Common Issues

- **"No matching sprite files found"**: Check filename convention (XXX-direction-variant-gender.ext)
- **Permission denied errors**: Close image viewers accessing the sprite files
- **Preview not showing**: Ensure processed sprites exist in output directory
- **Mod not working in-game**: Verify mod file structure and PokeMMO compatibility

### Debug Information

When reporting issues, include:

1. Log files from `logs/process.log`
2. Number of sprites being processed
3. Examples of problematic filenames
4. Operating system and available memory

## 📊 Performance

### Typical Results

Based on real usage data:

- **Mod File Size**: ~276 MB for complete sprite collection (Pokemon #001-711)
- **Processing Time**: Minutes for entire collections (1000+ sprites)
- **Quality**: No quality loss, canvas expansion preserves detail
- **Compatibility**: 100% PokeMMO compatible output
- **Memory Usage**: Efficient LRU caching with automatic cleanup
- **File Processing**: Background threaded analysis with progress indicators

### Performance Features

- **Batch Processing**: Handles entire sprite collections in single operations
- **Smart Caching**: LRU cache system with 50 image limit and automatic cleanup
- **Threaded Operations**: Non-blocking UI during file analysis and processing
- **Memory Management**: Proper cleanup of PIL images and tkinter objects
- **Progress Tracking**: Real-time progress bars and status updates
- **Error Recovery**: Automatic retry mechanisms for file permission issues

### Optimization Tips

- Use "Process All" for best performance with large collections
- Close other applications to free memory during processing
- Use SSD storage for faster file operations
- Enable "Show Logs" for detailed progress monitoring
- Use the limit option for testing with smaller sprite sets

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run from source: `python sprite_converter_gui.py`
4. Build executable: `python build_simple.py`

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Add comprehensive docstrings
- Include error handling and logging

## 📄 License

This tool is provided as-is for the PokeMMO community. Use responsibly and respect game terms of service.

## 🙏 Credits

Built for the PokeMMO community to revolutionize sprite mods with type weakness badges quick and easy.

**Special Thanks**:

- **Zoruah** - Original creator of the Bullseye mod and type weakness badge system that inspired this tool
- **UncleTyrone** - Creator of the Bullseye Injector project and the application you're looking at
- **4beemaster** - Refactored badge system, performance optimizations, and LaserFocus rebranding
- The PokeMMO community for inspiration and feedback
- All contributors who helped make this system possible

## 📞 Getting Help

If you encounter issues:

1. Check the log output in the GUI
2. Look at the `logs/process.log` file for detailed information
3. Verify your directory structure matches the expected format
4. Review the troubleshooting section above

For additional support, please refer to the PokeMMO modding community forums or create an issue in the project repository.

---

**LaserFocus Injector** - Making PokeMMO sprite modding accessible to everyone! 🎯
