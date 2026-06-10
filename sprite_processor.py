#!/usr/bin/env python3

"""Sprite replacement pipeline.

For each sprite in `TakeMoveTypeFrom`, detects the main Pokémon sprite bounding box
and replaces it with the corresponding image from `TakeSpriteFrom` while keeping the
badges intact. Outputs processed sprites and logs with bounding boxes.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple, Dict

from PIL import Image, ImageSequence

BoundingBox = Tuple[int, int, int, int]  # (left, top, right, bottom) with right/bottom exclusive





@dataclass
class Component:
    bbox: BoundingBox
    pixel_count: int



def parse_pokemon_info(filename: str) -> Tuple[Optional[str], Optional[str], bool]:
    """Parse Pokemon ID, sprite type (front/back), and shiny status from filename.
    
    Returns:
        Tuple of (pokemon_id, sprite_type, is_shiny)
        Example: '001-front-n-s.gif' -> ('001', 'front', True)
                 '025-back-n-m.gif' -> ('025', 'back', False)
    """
    # Pattern: <number>-<front|back>-<anything>-<s|s-m|s-f>.gif
    # Or without shiny: <number>-<front|back>-<anything>.gif
    match = re.match(r'^(\d+)-(front|back)-.*', filename.lower())
    if not match:
        return None, None, False
    
    pokemon_id = match.group(1)
    sprite_type = match.group(2)
    
    # Check for shiny: ends with -s, -s-m, or -s-f before extension
    name_without_ext = filename.rsplit('.', 1)[0].lower()
    is_shiny = name_without_ext.endswith('-s') or name_without_ext.endswith('-s-m') or name_without_ext.endswith('-s-f')
    
    return pokemon_id, sprite_type, is_shiny


def load_weaknesses_data(json_path: Path) -> Dict[str, List[Dict]]:
    """Load Pokemon weaknesses from JSON file."""
    with json_path.open('r', encoding='utf-8') as f:
        data = json.load(f)
    # Remove 'comment' key if present
    data.pop('comment', None)
    return data


def apply_sprite_limit(sprite_paths: List[Path], limit: int, process_back_sprites: bool, logger: logging.Logger) -> List[Path]:
    """Apply limit by unique Pokemon IDs to sprite paths.
    
    Args:
        sprite_paths: List of sprite file paths
        limit: Maximum number of unique Pokemon to process
        process_back_sprites: Whether back sprites are being processed with badges
        logger: Logger instance
    
    Returns:
        Filtered list of sprite paths
    """
    if process_back_sprites:
        # Limit applies to both front and back sprites
        logger.info("Limiting to %d unique Pokemon IDs (front and back sprites)", limit)
        seen_ids = set()
        limited_paths = []
        for sprite_path in sprite_paths:
            match = re.match(r'^(\d+)-', sprite_path.name)
            if match:
                pokemon_id = match.group(1)
                if pokemon_id not in seen_ids:
                    seen_ids.add(pokemon_id)
                    if len(seen_ids) > limit:
                        break
                if len(seen_ids) <= limit:
                    limited_paths.append(sprite_path)
        logger.info("Limited to %d sprites from %d unique Pokemon", len(limited_paths), len(seen_ids))
        return limited_paths
    else:
        # Limit only applies to front sprites; all back sprites are included
        logger.info("Limiting to %d unique Pokemon IDs (front sprites only)", limit)
        front_sprites = [p for p in sprite_paths if '-back-' not in p.name.lower()]
        back_sprites = [p for p in sprite_paths if '-back-' in p.name.lower()]
        
        seen_ids = set()
        limited_front = []
        for sprite_path in front_sprites:
            match = re.match(r'^(\d+)-', sprite_path.name)
            if match:
                pokemon_id = match.group(1)
                if pokemon_id not in seen_ids:
                    seen_ids.add(pokemon_id)
                    if len(seen_ids) > limit:
                        break
                if len(seen_ids) <= limit:
                    limited_front.append(sprite_path)
        
        logger.info("Limited front sprites to %d from %d unique Pokemon; including all %d back sprites", 
                   len(limited_front), len(seen_ids), len(back_sprites))
        return limited_front + back_sprites


def apply_shiny_hunter_filter(sprite_paths: List[Path], shiny_mode: str, logger: logging.Logger) -> List[Path]:
    """Apply Shiny Hunter Mode filtering to sprite paths.
    
    Args:
        sprite_paths: List of sprite file paths
        shiny_mode: Either "bullseye_normal" or "replacement_normal"
        logger: Logger instance
    
    Returns:
        Filtered list of sprite paths based on shiny mode
    """
    def is_shiny_front(filename: str) -> bool:
        """Check if sprite is a shiny front sprite (XXX-front-s-...)"""
        pattern = r'^\d{3}-front-s'
        return bool(re.match(pattern, filename))
    
    def is_normal_front(filename: str) -> bool:
        """Check if sprite is a normal front sprite (XXX-front-n-...)"""
        pattern = r'^\d{3}-front-n'
        return bool(re.match(pattern, filename))
    
    original_count = len(sprite_paths)
    
    if shiny_mode == "bullseye_normal":
        # Mode 1: Bullseye normals + Replacement shinies ONLY
        # Only process FRONT SHINY replacement sprites + all back sprites
        sprite_paths = [p for p in sprite_paths if is_shiny_front(p.name) or '-back-' in p.name]
        logger.info("✨ Shiny Hunter Mode 1: Filtered to %d sprites (shiny fronts + all backs, from %d total)", 
                   len(sprite_paths), original_count)
        logger.info("📋 Normal front sprites will use Bullseye originals")
        
    elif shiny_mode == "replacement_normal":
        # Mode 2: Replacement normals + Bullseye shinies
        # Only process FRONT NORMAL replacement sprites + all back sprites
        sprite_paths = [p for p in sprite_paths if is_normal_front(p.name) or '-back-' in p.name]
        logger.info("✨ Shiny Hunter Mode 2: Filtered to %d sprites (normal fronts + all backs, from %d total)", 
                   len(sprite_paths), original_count)
        logger.info("📋 Shiny front sprites will use Bullseye originals")
    
    return sprite_paths


def scan_sprite_heights(sprite_paths: List[Path], logger: logging.Logger) -> Tuple[float, float]:
    """Scan all sprites to determine max heights for badge scaling.
    
    Args:
        sprite_paths: List of sprite file paths to scan
        logger: Logger instance
    
    Returns:
        Tuple of (max_front_height, max_back_height)
    """
    logger.info("Scanning sprites for max heights (fast dimension check)")
    
    max_front_height = 0
    max_back_height = 0
    max_front_sprite = ""
    max_back_sprite = ""
    front_count = 0
    back_count = 0
    
    for sprite_path in sprite_paths:
        pokemon_id, sprite_type, _ = parse_pokemon_info(sprite_path.name)
        if not pokemon_id or not sprite_type:
            continue
        
        try:
            # Fast dimension check - only reads image header, doesn't decode pixels
            with Image.open(sprite_path) as img:
                height = img.height
                
                if sprite_type == 'front':
                    if height > max_front_height:
                        max_front_height = height
                        max_front_sprite = sprite_path.name
                    front_count += 1
                elif sprite_type == 'back':
                    if height > max_back_height:
                        max_back_height = height
                        max_back_sprite = sprite_path.name
                    back_count += 1
        except Exception as exc:
            logger.warning("%s: failed to read dimensions - %s", sprite_path.name, exc)
    
    logger.info("Scanned %d front sprites - Max height: %dpx (from %s)", front_count, max_front_height, max_front_sprite)
    logger.info("Scanned %d back sprites - Max height: %dpx (from %s)", back_count, max_back_height, max_back_sprite)
    
    return max_front_height, max_back_height


def calculate_badge_and_min_heights(max_front_height: float, max_back_height: float, logger: logging.Logger,
                                    badge_height_override: Optional[float] = None,
                                    min_height_override: Optional[float] = None,
                                    pre_badge_scale: float = 100.0) -> Tuple[float, float, float]:
    """Calculate target badge heights and minimum front sprite height.
    
    Args:
        max_front_height: Maximum height of front sprites (already scaled if pre_badge_scale applied)
        max_back_height: Maximum height of back sprites (already scaled if pre_badge_scale applied)
        logger: Logger instance
        badge_height_override: Optional manual override for badge height
        min_height_override: Optional manual override for minimum sprite height
        pre_badge_scale: Pre-badge scale percentage (100 = no scale), used to scale the minimum height floor
    
    Returns:
        Tuple of (target_front_badge_height, target_back_badge_height, min_front_height)
    """
    # Calculate scale factor for minimum height floor
    scale_factor = pre_badge_scale / 100.0 if pre_badge_scale > 0 else 1.0
    
    # Calculate or use override for badge heights
    if badge_height_override is not None:
        target_front_badge_height = badge_height_override
        target_back_badge_height = badge_height_override
        logger.info("Using manual badge height override: %.1f", badge_height_override)
    else:
        # Calculate target badge heights (1/8th of max height for each type, minimum 15px absolute)
        min_badge = 15.0  # Absolute minimum for readability
        target_front_badge_height = max(min_badge, max_front_height / 8.0) if max_front_height > 0 else 38.0 * scale_factor
        target_back_badge_height = max(min_badge, max_back_height / 8.0) if max_back_height > 0 else 38.0 * scale_factor
    
    # Calculate or use override for minimum sprite height
    if min_height_override is not None:
        # Scale the override by pre_badge_scale
        min_front_height = min_height_override * scale_factor
        logger.info("Using manual minimum height override: %.1f (scaled from %.1f)", min_front_height, min_height_override)
    else:
        # Calculate minimum front sprite height (100px scaled or 51% of max front height, whichever is greater)
        min_floor = 100.0 * scale_factor
        min_front_height = max(min_floor, max_front_height * 0.51) if max_front_height > 0 else min_floor
    
    logger.info("Target badge heights - Front: %.1f, Back: %.1f", target_front_badge_height, target_back_badge_height)
    logger.info("Minimum front sprite height: %.1f", min_front_height)
    
    return target_front_badge_height, target_back_badge_height, min_front_height


def copy_bullseye_sprites_as_fallback(bullseye_dir: Path, output_dir: Path, logger: logging.Logger) -> int:
    """Batch copy all Bullseye sprites to output directory as fallback.
    
    Args:
        bullseye_dir: Directory containing Bullseye sprites
        output_dir: Destination directory
        logger: Logger instance
    
    Returns:
        Number of sprites copied
    
    Raises:
        FileNotFoundError: If bullseye_dir doesn't exist
    """
    if not bullseye_dir.exists():
        error_msg = f"Bullseye sprites directory not found: {bullseye_dir}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    import shutil
    logger.info("Batch copying Bullseye sprites to output directory as fallback...")
    bullseye_paths = sorted(p for p in bullseye_dir.iterdir() if p.is_file() and p.suffix.lower() in ['.gif', '.png'])
    copied_count = 0
    output_dir.mkdir(parents=True, exist_ok=True)
    for bullseye_path in bullseye_paths:
        try:
            output_path = output_dir / bullseye_path.name
            if not output_path.exists():  # Only copy if not already present
                shutil.copy2(bullseye_path, output_path)
                copied_count += 1
        except Exception as exc:
            logger.warning("Failed to copy Bullseye sprite %s: %s", bullseye_path.name, exc)
    logger.info("Copied %d Bullseye sprites as fallback", copied_count)
    return copied_count


def separate_front_back_sprites(sprite_paths: List[Path]) -> Tuple[List[Path], List[Path]]:
    """Separate sprite paths into front and back sprites.
    
    Args:
        sprite_paths: List of sprite file paths
    
    Returns:
        Tuple of (front_sprites, back_sprites)
    """
    front_sprites = [p for p in sprite_paths if '-back-' not in p.name.lower()]
    back_sprites = [p for p in sprite_paths if '-back-' in p.name.lower()]
    return front_sprites, back_sprites


def bulk_copy_back_sprites(back_sprites: List[Path], output_dir: Path, logger: logging.Logger, results: dict) -> int:
    """Bulk copy back sprites without badge processing.
    
    Args:
        back_sprites: List of back sprite paths to copy
        output_dir: Destination directory
        logger: Logger instance
        results: Results dictionary to track copied sprites
    
    Returns:
        Number of sprites copied
    """
    import shutil
    logger.info("Bulk copying %d back sprites without badge processing...", len(back_sprites))
    copied_count = 0
    output_dir.mkdir(parents=True, exist_ok=True)
    for back_sprite in back_sprites:
        try:
            output_path = output_dir / back_sprite.name
            shutil.copy2(back_sprite, output_path)
            # Track bulk-copied back sprites in results (for scale tables)
            results[back_sprite.name] = str(output_path)
            copied_count += 1
        except Exception as exc:
            logger.warning("Failed to copy %s: %s", back_sprite.name, exc)
    logger.info("Batch copied %d back sprites (no badges)", copied_count)
    return copied_count


def determine_sprites_to_process(sprite_paths: List[Path], front_sprites: List[Path], 
                                 process_back_sprites: bool, logger: logging.Logger) -> List[Path]:
    """Determine which sprites to process with badges based on settings.
    
    Args:
        sprite_paths: All sprite paths
        front_sprites: Front sprite paths only
        process_back_sprites: Whether to process back sprites with badges
        logger: Logger instance
    
    Returns:
        List of sprite paths to process with badges
    """
    if process_back_sprites:
        logger.info("Processing all sprites (front and back) with badges")
        return sprite_paths
    else:
        logger.info("Processing front sprites with badges")
        return front_sprites


def save_processing_summary(results: dict, log_dir: Path, logger: logging.Logger) -> None:
    """Save processing results summary to JSON file.
    
    Args:
        results: Dictionary of processing results
        log_dir: Directory to save summary
        logger: Logger instance
    """
    summary_path = log_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as fh:
        json.dump(results, fh, indent=2)
    logger.info("Wrote processing summary to %s", summary_path)
    logger.info("Completed sprite processing (%d successful)", len(results))


def load_badge_image(badges_dir: Path, type_name: str, multiplier: int) -> Optional[Image.Image]:
    """Load a badge image from the badges directory.
    
    Args:
        badges_dir: Path to badges directory
        type_name: Pokemon type (e.g., 'Fire', 'Water')
        multiplier: Damage multiplier (2 or 4)
    
    Returns:
        Badge image in RGBA mode, or None if not found
    """
    if multiplier == 4:
        badge_filename = f"{type_name}-4.png"
    else:
        badge_filename = f"{type_name}.png"
    
    badge_path = badges_dir / badge_filename
    if not badge_path.exists():
        return None
    
    return load_rgba_image(badge_path)


def get_badges_for_pokemon(pokemon_id: str, is_shiny: bool, weaknesses_data: Dict, badges_dir: Path) -> List[Image.Image]:
    """Get list of badge images for a Pokemon based on its weaknesses.
    
    Args:
        pokemon_id: Pokemon ID as string (e.g., '001')
        is_shiny: Whether this is a shiny variant
        weaknesses_data: Loaded weaknesses dictionary
        badges_dir: Path to badges directory
    
    Returns:
        List of badge images ordered: shiny (if applicable), 4x weaknesses, then 2x weaknesses
    """
    badges = []
    
    # Add shiny badge first if this is a shiny variant
    if is_shiny:
        shiny_path = badges_dir / "Shiny.png"
        if shiny_path.exists():
            badges.append(load_rgba_image(shiny_path))
    
    # Get type weakness badges and sort by multiplier (4x first, then 2x)
    if pokemon_id in weaknesses_data:
        weaknesses = weaknesses_data[pokemon_id]
        
        # Sort weaknesses: 4x multiplier first, then 2x
        sorted_weaknesses = sorted(weaknesses, key=lambda w: w.get('multiplier', 2), reverse=True)
        
        for weakness in sorted_weaknesses:
            type_name = weakness.get('type')
            multiplier = weakness.get('multiplier', 2)
            
            badge_img = load_badge_image(badges_dir, type_name, multiplier)
            if badge_img:
                badges.append(badge_img)
    
    return badges



def configure_logging(log_dir: Path) -> logging.Logger:

    """Configure a logger that writes to file and stdout."""

    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("sprite_processor")

    logger.setLevel(logging.INFO)

    # Clear any default handlers to avoid duplicated logs when re-running.

    logger.handlers.clear()



    log_path = log_dir / "process.log"

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")

    console_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler.setFormatter(formatter)

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger





def load_rgba_image(path: Path) -> Image.Image:

    """Load an image and ensure it is in RGBA mode."""

    with Image.open(path) as img:

        return img.convert("RGBA")





def load_animated_rgba_frames(path: Path) -> Tuple[List[Image.Image], List[int], int, List[int]]:
    """Load all frames from an image as RGBA along with timing metadata."""
    with Image.open(path) as img:
        loop = (img.info.get("loop", 0) or 0)
        default_duration = img.info.get("duration", 100) or 100
        default_disposal = img.info.get("disposal", 2)

        frames: List[Image.Image] = []
        durations: List[int] = []
        disposals: List[int] = []

        for frame in ImageSequence.Iterator(img):
            duration = frame.info.get("duration", default_duration) or default_duration
            durations.append(duration)
            disposals.append(frame.info.get("disposal", default_disposal))
            frames.append(frame.convert("RGBA"))

        if not frames:
            frames.append(img.convert("RGBA"))
            durations.append(default_duration)
            disposals.append(default_disposal)

    return frames, durations, loop, disposals



def union_frame_bbox(frames: Iterable[Image.Image]) -> Optional[BoundingBox]:
    """Return the union bounding box of non-transparent pixels across frames."""
    boxes = [frame.getbbox() for frame in frames if frame.getbbox()]
    if not boxes:
        return None

    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[2] for box in boxes)
    bottom = max(box[3] for box in boxes)
    return left, top, right, bottom



def resize_animation_frames(frames: List[Image.Image], size: Tuple[int, int]) -> List[Image.Image]:
    """Resize an animated sequence to the target size while keeping alignment."""
    if size[0] <= 0 or size[1] <= 0:
        raise ValueError(f"Invalid resize dimensions: {size}")

    content_bbox = union_frame_bbox(frames)
    resized_frames: List[Image.Image] = []
    for frame in frames:
        working = frame
        if content_bbox:
            working = frame.crop(content_bbox)
        # Use smart resampling: NEAREST for integer scaling, LANCZOS for non-integer
        scale_x = size[0] / working.width
        scale_y = size[1] / working.height
        if scale_x == int(scale_x) and scale_y == int(scale_y) and scale_x >= 1.0 and scale_y >= 1.0:
            # Integer upscaling - use NEAREST for crisp pixel art
            resized_frames.append(working.resize(size, Image.Resampling.NEAREST))
        else:
            # Non-integer scaling - use LANCZOS for smoother results
            resized_frames.append(working.resize(size, Image.Resampling.LANCZOS))
    return resized_frames


def resize_animation_frames_preserve_aspect(frames: List[Image.Image], max_size: Tuple[int, int]) -> List[Image.Image]:
    """Resize an animated sequence to fit well within max_size while preserving aspect ratio."""
    if max_size[0] <= 0 or max_size[1] <= 0:
        raise ValueError(f"Invalid max dimensions: {max_size}")

    # Get the union bounding box across ALL frames to account for animation movement
    content_bbox = union_frame_bbox(frames)
    if not content_bbox:
        return frames
    
    # Calculate the scale required to fit within the requested max size
    max_width, max_height = max_size
    bbox_width = content_bbox[2] - content_bbox[0]
    bbox_height = content_bbox[3] - content_bbox[1]
    scale_limit = min(max_width / bbox_width, max_height / bbox_height)
    scale = min(1.0, scale_limit)

    resized_frames: List[Image.Image] = []
    for frame in frames:
        working = frame.crop(content_bbox)

        if scale < 1.0:
            new_width = max(1, int(round(working.size[0] * scale)))
            new_height = max(1, int(round(working.size[1] * scale)))
            resized_frames.append(working.resize((new_width, new_height), Image.Resampling.LANCZOS))
        else:
            resized_frames.append(working.copy())
    return resized_frames



def normalize_durations(durations: List[int], frame_count: int, fallback: int = 100) -> List[int]:
    """Ensure the duration list matches the number of frames."""
    if frame_count <= 0:
        return []

    if not durations:
        durations = [fallback] * frame_count
    else:
        durations = [duration or fallback for duration in durations]

    if len(durations) < frame_count:
        durations.extend([durations[-1]] * (frame_count - len(durations)))
    elif len(durations) > frame_count:
        durations = durations[:frame_count]

    return durations



def extract_components(alpha: Image.Image) -> List[Component]:

    """Return connected components for the alpha channel using 4-neighbourhood."""

    w, h = alpha.size

    pixels = alpha.load()

    visited = [[False] * w for _ in range(h)]

    components: List[Component] = []



    for y in range(h):

        for x in range(w):

            if visited[y][x]:

                continue

            visited[y][x] = True

            # Use a higher threshold to filter out very low alpha values (likely artifacts)
            if pixels[x, y] < 32:  # Only consider pixels with alpha >= 32 (out of 255)

                continue



            stack = [(x, y)]

            min_x = max_x = x

            min_y = max_y = y

            count = 0



            while stack:

                cx, cy = stack.pop()

                count += 1

                if cx < min_x:

                    min_x = cx

                if cx > max_x:

                    max_x = cx

                if cy < min_y:

                    min_y = cy

                if cy > max_y:

                    max_y = cy



                for nx, ny in ((cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)):

                    if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:

                        visited[ny][nx] = True

                        # Use the same threshold for connected components
                        if pixels[nx, ny] >= 32:

                            stack.append((nx, ny))



            bbox: BoundingBox = (min_x, min_y, max_x + 1, max_y + 1)

            components.append(Component(bbox=bbox, pixel_count=count))



    components.sort(key=lambda comp: comp.pixel_count, reverse=True)

    return components





def classify_components(components: Iterable[Component], min_pixel_threshold: int = 100) -> Tuple[Optional[Component], List[Component]]:

    """Return the largest component as the main sprite; only small, corner-positioned components as badges.

    Filters out very small components and large secondary components (like cloud effects) that should not be preserved.
    
    Special handling for small sprites like Unown where badges may be larger than the sprite itself.

    Args:

        components: List of detected components

        min_pixel_threshold: Minimum pixel count for a component to be considered valid

    """

    comps = list(components)

    if not comps:

        return None, []

    # Filter out very small components (likely runaway pixels)

    valid_comps = [comp for comp in comps if comp.pixel_count >= min_pixel_threshold]

    if not valid_comps:

        # If no components meet the threshold, fall back to the largest one

        valid_comps = [comps[0]]

    main = valid_comps[0]
    
    # Look for badges specifically in the bottom-right area
    # Strategy: Start from the bottom-most component and search upward
    # This ensures we only get actual badges, not Pokemon body parts
    
    potential_badges = valid_comps[1:]  # All components except the main one
    
    if not potential_badges:
        return main, []
    
    # Get the main sprite's bounding box for reference
    main_left, main_top, main_right, main_bottom = main.bbox
    
    # Filter components to only those on the right side
    # Badges should be to the right of the main sprite
    # Don't filter by vertical position since badge stacks can be taller than the Pokemon
    right_side_candidates = []
    
    for comp in potential_badges:
        comp_left, comp_top, comp_right, comp_bottom = comp.bbox
        
        # Badge must be to the right of the main sprite (or mostly to the right)
        # Use a generous threshold to catch badges that might slightly overlap
        is_right_side = comp_left >= main_right * 0.6  # Component starts at or past 60% of main sprite's right edge
        
        # Size check: badges should be reasonably sized (not huge background elements)
        is_reasonable_size = comp.pixel_count <= 5000
        
        if is_right_side and is_reasonable_size:
            right_side_candidates.append(comp)
    
    # Sort candidates by bottom position (lowest first), then by right position
    # This ensures we start with the bottom-most badge
    right_side_candidates.sort(key=lambda comp: (comp.bbox[3], comp.bbox[2]), reverse=True)
    
    # Take only components that form a vertical stack from bottom-right
    # Start with the bottom-most component and work upward
    badges = []
    if right_side_candidates:
        # Always take the bottom-most component as it's most likely a badge
        badges.append(right_side_candidates[0])
        
        # Check remaining components - only add if they're above the previous badge
        for comp in right_side_candidates[1:]:
            if comp.bbox[3] < badges[-1].bbox[1]:  # This component's bottom is above the last badge's top
                badges.append(comp)
    
    # Sort badges top to bottom for proper rendering order
    badges.sort(key=lambda comp: comp.bbox[1])

    return main, badges





def crop_to_content(image: Image.Image) -> Image.Image:

    """Crop the image to the bounding box of non-transparent pixels."""

    alpha = image.split()[3]

    bbox = alpha.getbbox()

    if bbox is None:

        return image

    return image.crop(bbox)


def clean_edge_pixels(image: Image.Image, bbox: BoundingBox, cleanup_radius: int = 2) -> Image.Image:

    """Clean up edge pixels around a bounding box to remove stray pixels."""

    result = image.copy()

    left, top, right, bottom = bbox

    

    # Expand the cleanup area slightly beyond the bounding box

    cleanup_left = max(0, left - cleanup_radius)

    cleanup_top = max(0, top - cleanup_radius)

    cleanup_right = min(image.width, right + cleanup_radius)

    cleanup_bottom = min(image.height, bottom + cleanup_radius)

    

    # Create a mask for the cleanup area

    mask = Image.new('L', image.size, 0)

    cleanup_mask = Image.new('L', (cleanup_right - cleanup_left, cleanup_bottom - cleanup_top), 255)

    mask.paste(cleanup_mask, (cleanup_left, cleanup_top))

    

    # Clear the cleanup area

    transparent = Image.new('RGBA', (cleanup_right - cleanup_left, cleanup_bottom - cleanup_top), (0, 0, 0, 0))

    result.paste(transparent, (cleanup_left, cleanup_top), cleanup_mask)

    

    return result


def aggressive_background_cleanup(image: Image.Image, preserve_components: List[Component]) -> Image.Image:

    """Aggressively clean the background, only preserving specified components."""

    result = Image.new('RGBA', image.size, (0, 0, 0, 0))

    

    # Only preserve the specified components

    for component in preserve_components:

        component_img = image.crop(component.bbox)

        result.paste(component_img, (component.bbox[0], component.bbox[1]), component_img)

    

    return result





def resize_sprite(sprite: Image.Image, size: Tuple[int, int]) -> Image.Image:

    """Resize sprite to target size using high-quality resampling."""

    if size[0] <= 0 or size[1] <= 0:

        raise ValueError(f"Invalid resize dimensions: {size}")

    cropped = crop_to_content(sprite)

    # Use smart resampling: NEAREST for integer scaling, LANCZOS for non-integer
    scale_x = size[0] / cropped.width
    scale_y = size[1] / cropped.height
    if scale_x == int(scale_x) and scale_y == int(scale_y) and scale_x >= 1.0 and scale_y >= 1.0:
        # Integer upscaling - use NEAREST for crisp pixel art
        return cropped.resize(size, Image.Resampling.NEAREST)
    else:
        # Non-integer scaling - use LANCZOS for smoother results
        return cropped.resize(size, Image.Resampling.LANCZOS)





def paste_sprite(base: Image.Image, sprite: Image.Image, bbox: BoundingBox) -> Image.Image:

    """Paste the sprite into the base image at the provided bounding box."""

    left, top, right, bottom = bbox

    width = right - left

    height = bottom - top

    if sprite.size != (width, height):

        # Use smart resampling: NEAREST for integer scaling, LANCZOS for non-integer
        scale_x = width / sprite.width
        scale_y = height / sprite.height
        if scale_x == int(scale_x) and scale_y == int(scale_y) and scale_x >= 1.0 and scale_y >= 1.0:
            # Integer upscaling - use NEAREST for crisp pixel art
            sprite = sprite.resize((width, height), Image.Resampling.NEAREST)
        else:
            # Non-integer scaling - use LANCZOS for smoother results
            sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)

    result = base.copy()

    result.paste(sprite, (left, top), sprite)

    return result





def process_pair(sprite_path: Path, output_dir: Path, logger: logging.Logger, 
                badges_dir: Path, weaknesses_data: Dict, target_badge_height: float,
                min_front_height: float = 0, badge_location: str = "right",
                padding_mode: str = "left", custom_padding: Optional[int] = None,
                pre_badge_scale: float = 100.0, skip_badges: bool = False) -> Optional[dict]:
    """Process a single sprite and add badges from the badges directory.
    
    Args:
        sprite_path: Path to the replacement sprite
        output_dir: Directory to save processed sprite
        logger: Logger instance
        badges_dir: Path to badges directory
        weaknesses_data: Loaded Pokemon weaknesses data
        target_badge_height: Target height for badges (1/8th of max sprite height)
        min_front_height: Minimum height for front sprites (51% of max front height)
        badge_location: Where to place badges - "left" or "right" (default: right)
        padding_mode: Centering mode - "left" (padding on left), "right" (padding on right), 
                     or "none" (no centering padding).
        custom_padding: Custom padding in pixels. If None, uses badge_width + gap for centering.
        pre_badge_scale: Scale percentage to apply before badges are added (100 = no change).
        skip_badges: If True, skip adding badges (useful for shiny hunter mode).
    """
    # Parse Pokemon info from filename
    pokemon_id, sprite_type, is_shiny = parse_pokemon_info(sprite_path.name)
    if not pokemon_id or not sprite_type:
        logger.warning("%s: unable to parse Pokemon ID or sprite type from filename", sprite_path.name)
        return None

    if not sprite_path.exists():
        logger.warning("%s: sprite file not found", sprite_path.name)
        return None

    replacement_frames, durations, loop, _ = load_animated_rgba_frames(sprite_path)
    
    # Apply pre-badge scaling if not 100%
    if pre_badge_scale != 100.0 and pre_badge_scale > 0:
        scale_factor = pre_badge_scale / 100.0
        pre_scale_size = (replacement_frames[0].width, replacement_frames[0].height)
        scaled_frames = []
        for frame in replacement_frames:
            new_width = max(1, int(frame.width * scale_factor))
            new_height = max(1, int(frame.height * scale_factor))
            # Use NEAREST for pixel art to maintain crisp edges
            scaled_frame = frame.resize((new_width, new_height), Image.Resampling.NEAREST)
            scaled_frames.append(scaled_frame)
        replacement_frames = scaled_frames
        logger.info("%s: applied pre-badge scale %.0f%% (%dx%d -> %dx%d)", 
                   sprite_path.name, pre_badge_scale,
                   pre_scale_size[0], pre_scale_size[1],
                   replacement_frames[0].width, replacement_frames[0].height)
    
    # Check that sprite has content
    replacement_bbox = union_frame_bbox(replacement_frames)
    if not replacement_bbox:
        logger.warning("%s: sprite has no content", sprite_path.name)
        return None
    
    # Use scaled frame dimensions
    replacement_width = replacement_frames[0].width
    replacement_height = replacement_frames[0].height
    
    # Load badges for this Pokemon (skip if skip_badges is True)
    if skip_badges:
        badge_images = []
        logger.info("%s: Skipping badges (skip_badges enabled)", sprite_path.name)
    else:
        badge_images = get_badges_for_pokemon(pokemon_id, is_shiny, weaknesses_data, badges_dir)
    
    # Prepare badge layers - scale to target height
    badge_layers = []
    total_badge_height = 0
    max_badge_width = 0
    
    for badge_img in badge_images:
        # Trim transparent whitespace around the badge
        alpha = badge_img.split()[3]
        trim_bbox = alpha.getbbox()
        if trim_bbox:
            badge_img = badge_img.crop(trim_bbox)
        
        # Calculate scale to achieve target badge height
        original_badge_height = badge_img.height
        original_badge_width = badge_img.width
        
        if original_badge_height > 0:
            badge_scale = target_badge_height / original_badge_height
            scaled_badge_width = int(original_badge_width * badge_scale)
            scaled_badge_height = int(original_badge_height * badge_scale)
            
            # Resize the badge using smart resampling
            if badge_scale == int(badge_scale) and badge_scale >= 1.0:
                # Integer upscaling - use NEAREST for crisp pixel art
                badge_img = badge_img.resize((scaled_badge_width, scaled_badge_height), Image.Resampling.NEAREST)
            else:
                # Non-integer scaling - use LANCZOS for smoother results
                badge_img = badge_img.resize((scaled_badge_width, scaled_badge_height), Image.Resampling.LANCZOS)
            
            # Track badge dimensions for canvas calculation
            total_badge_height += scaled_badge_height
            max_badge_width = max(max_badge_width, scaled_badge_width)
            
            badge_layers.append(badge_img)
    
    # Get the actual replacement GIF dimensions (original size with padding preserved)
    gif_width = replacement_frames[0].width if replacement_frames else 0
    gif_height = replacement_frames[0].height if replacement_frames else 0
    
    # Calculate gap for type indicators
    desired_gap = 2  # 2px gap between GIF and badges
    
    # Calculate canvas dimensions based on badge location and padding mode
    # - badge_location: "left" or "right" - where badges appear
    # - padding_mode: "left", "right", or "none" - where centering padding appears
    badge_space = (max_badge_width + desired_gap) if badge_layers else 0
    
    # Use custom padding if provided, otherwise use badge_space for centering
    centering_padding = custom_padding if custom_padding is not None else badge_space
    
    # Calculate left and right space based on badge location and padding mode
    if badge_location == "left":
        # Badges on left side
        left_badge_space = badge_space
        right_badge_space = 0
        if padding_mode == "left":
            # Centering padding on left (before badges)
            left_padding_extra = centering_padding
            right_padding_extra = 0
        elif padding_mode == "right":
            # Centering padding on right
            left_padding_extra = 0
            right_padding_extra = centering_padding
        else:  # "none"
            left_padding_extra = 0
            right_padding_extra = 0
        left_padding = left_padding_extra + left_badge_space
        right_padding = right_padding_extra
    else:  # badge_location == "right"
        # Badges on right side
        left_badge_space = 0
        right_badge_space = badge_space
        if padding_mode == "left":
            # Centering padding on left
            left_padding = centering_padding
            right_padding = right_badge_space
        elif padding_mode == "right":
            # Centering padding on right (after badges)
            left_padding = 0
            right_padding = right_badge_space + centering_padding
        else:  # "none"
            left_padding = 0
            right_padding = right_badge_space
    
    canvas_width = left_padding + gif_width + right_padding
    
    # Initial height is just gif + badges (bottom-aligned)
    initial_height = max(gif_height, total_badge_height)
    
    # Step 2: Apply minimum height rules for front sprites
    if sprite_type == 'front' and min_front_height > 0:
        if initial_height < min_front_height:
            # Add TOP padding to reach minimum
            canvas_height = min_front_height
        else:
            # Add BOTTOM padding equal to (initial_height - min_front_height)
            canvas_height = initial_height + (initial_height - min_front_height)
    else:
        canvas_height = initial_height
    
    # Convert to integers for PIL Image.new()
    canvas_width = int(canvas_width)
    canvas_height = int(canvas_height)
    initial_height = int(initial_height)

    # Create base canvas with static badges
    base_canvas = Image.new("RGBA", (canvas_width, canvas_height))
    
    # Calculate badge positions once - they stay static across all frames
    gif_left = left_padding  # GIF starts after left padding
    gif_right = gif_left + gif_width  # Right edge of GIF
    
    # Positioning logic:
    # If TOP padding: bottom-align to final canvas (gif_top = canvas_height - gif_height)
    # If BOTTOM padding: bottom-align to initial canvas (gif_top = initial_height - gif_height)
    if sprite_type == 'front' and min_front_height > 0 and initial_height < min_front_height:
        # Top padding added - bottom-align to final canvas
        gif_top = canvas_height - gif_height
    else:
        # Bottom padding added OR no padding - bottom-align to initial canvas
        gif_top = initial_height - gif_height
    
    gif_bottom = gif_top + gif_height
    
    gap = desired_gap
    # Calculate badge X position based on badge_location
    if badge_location == "left":
        # Badges on left side of the sprite
        # Badges are placed after any centering padding but before the gap to sprite
        if padding_mode == "left":
            badge_x = centering_padding  # After centering padding, badges start here
        else:
            badge_x = 0  # At the left edge
    else:  # badge_location == "right"
        # Badges on right side of the sprite
        badge_x = gif_right + gap
    badge_y_position = gif_bottom  # Badges align to bottom of GIF
    
    # Paste static badges onto base canvas (reverse order for proper stacking)
    for badge_img in reversed(badge_layers):
        badge_height = badge_img.height
        badge_y_position -= badge_height
        base_canvas.paste(badge_img, (badge_x, badge_y_position), badge_img)

    # Create all frames with GIF + badges on the canvas
    output_frames: List[Image.Image] = []
    for i, frame in enumerate(replacement_frames):
        canvas = base_canvas.copy()  # Start with base that has badges already
        
        # Position the GIF using pre-calculated position
        frame_width, frame_height = frame.size
        
        paste_x = left_padding
        paste_y = gif_top  # Use pre-calculated position from badge placement logic
        
        # Use the frame as both image and mask for cleaner pasting
        # Badges are already on the base canvas, so we just paste the animated GIF frame
        canvas.paste(frame, (paste_x, paste_y), frame)
        
        output_frames.append(canvas)

    # Apply 2px transparent border padding around the final sprite
    padded_frames = []
    border_padding = 2
    for frame in output_frames:
        padded_width = frame.width + (border_padding * 2)
        padded_height = frame.height + (border_padding * 2)
        padded_frame = Image.new("RGBA", (padded_width, padded_height), (0, 0, 0, 0))
        padded_frame.paste(frame, (border_padding, border_padding), frame)
        padded_frames.append(padded_frame)
    output_frames = padded_frames
    
    # Update canvas dimensions for logging
    canvas_width = output_frames[0].width
    canvas_height = output_frames[0].height

    durations = normalize_durations(durations, len(output_frames))
    loop = loop or 0

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / sprite_path.name

    output_frames[0].save(
        output_path,
        save_all=True,
        append_images=output_frames[1:],
        loop=loop,
        duration=durations,
        disposal=2,
    )

    logger.info(
        "%s: composited sprite (canvas=%dx%d, badges=%d) -> %s",
        sprite_path.name,
        canvas_width,
        canvas_height,
        len(badge_layers),
        output_path,
    )

    return {
        "pokemon_id": pokemon_id,
        "sprite_type": sprite_type,
        "is_shiny": is_shiny,
        "output_path": str(output_path),
        "canvas_size": (canvas_width, canvas_height),
        "badge_count": len(badge_layers),
    }



def run_pipeline(sprite_dir: Path, output_dir: Path, log_dir: Path, badges_dir: Path, 
                weaknesses_json: Path, bullseye_dir: Path, limit: Optional[int] = None, 
                 process_back_sprites: bool = False, shiny_hunter_mode: Optional[str] = None,
                 badge_height_override: Optional[float] = None, min_height_override: Optional[float] = None,
                 use_bullseye_fallback: bool = True,
                 create_summary_table: bool = True, create_front_table: bool = True, create_back_table: bool = True,
                 badge_location: str = "right", padding_mode: str = "left", custom_padding: Optional[int] = None,
                 ignore_back_sprites: bool = False, pre_badge_scale: float = 100.0) -> None:

    logger = configure_logging(log_dir)
    logger.info("Starting sprite processing")
    logger.info("Back sprite badge processing: %s", "enabled" if process_back_sprites else "disabled")
    if ignore_back_sprites:
        logger.info("Ignore back sprites: ENABLED - back sprites will be skipped entirely")
    if pre_badge_scale != 100.0:
        logger.info("Pre-badge scale: %.0f%%", pre_badge_scale)
        logger.info("Ignore back sprites: ENABLED - back sprites will be skipped entirely")
    logger.info("Badge location: %s", badge_location)
    logger.info("Padding mode: %s", padding_mode)
    if custom_padding is not None:
        logger.info("Custom padding: %dpx", custom_padding)
    
    if shiny_hunter_mode:
        logger.info("✨ Shiny Hunter Mode ENABLED: %s", shiny_hunter_mode)

    # Load weaknesses data
    logger.info("Loading weaknesses data from %s", weaknesses_json)
    weaknesses_data = load_weaknesses_data(weaknesses_json)
    logger.info("Loaded weaknesses for %d Pokemon", len(weaknesses_data))

    # Batch copy all Bullseye sprites to output directory as fallback (if enabled)
    if use_bullseye_fallback:
        copy_bullseye_sprites_as_fallback(bullseye_dir, output_dir, logger)
    else:
        logger.info("📋 Bullseye fallback disabled - only replacement sprites will be used")

    # Get all replacement sprite files
    sprite_paths = sorted(p for p in sprite_dir.iterdir() if p.is_file() and p.suffix.lower() in ['.gif', '.png'])

    # Scan all sprites to determine max heights for badge scaling BEFORE filtering
    # This ensures consistent badge sizing regardless of shiny hunter mode or limit
    max_front_height, max_back_height = scan_sprite_heights(sprite_paths, logger)

    # Apply pre-badge scale to max heights for badge calculation
    # This ensures badges are sized for the final scaled output
    if pre_badge_scale != 100.0 and pre_badge_scale > 0:
        scale_factor = pre_badge_scale / 100.0
        scaled_front_height = max_front_height * scale_factor
        scaled_back_height = max_back_height * scale_factor
        logger.info("Applying %.0f%% scale to height calculations: front %d->%d, back %d->%d",
                   pre_badge_scale, max_front_height, int(scaled_front_height), 
                   max_back_height, int(scaled_back_height))
        max_front_height = scaled_front_height
        max_back_height = scaled_back_height

    # Apply Shiny Hunter Mode filtering AFTER scanning heights
    if shiny_hunter_mode:
        sprite_paths = apply_shiny_hunter_filter(sprite_paths, shiny_hunter_mode, logger)

    # Apply limit by unique Pokemon IDs if specified
    if limit is not None:
        sprite_paths = apply_sprite_limit(sprite_paths, limit, process_back_sprites, logger)
    
    # Calculate target badge heights and minimum front sprite height
    target_front_badge_height, target_back_badge_height, min_front_height = calculate_badge_and_min_heights(
        max_front_height, max_back_height, logger, badge_height_override, min_height_override, pre_badge_scale
    )

    # Separate front and back sprites
    front_sprites, back_sprites = separate_front_back_sprites(sprite_paths)
    
    # Check if we should ignore back sprites entirely
    if ignore_back_sprites:
        logger.info("Ignoring %d back sprites (ignore back sprites enabled)", len(back_sprites))
        back_sprites = []  # Clear back sprites list
    
    logger.info("Found %d front sprites and %d back sprites", len(front_sprites), len(back_sprites))
    
    # Initialize results dictionary to track all processed sprites
    results = {}
    
    # If not processing back sprites with badges, bulk copy them first
    if not process_back_sprites and back_sprites:
        bulk_copy_back_sprites(back_sprites, output_dir, logger, results)
    
    # Determine which sprites to process with badges
    sprites_to_process = determine_sprites_to_process(sprite_paths, front_sprites, process_back_sprites, logger)
    
    # Process sprites with badges
    for sprite_path in sprites_to_process:
        pokemon_id, sprite_type, is_shiny = parse_pokemon_info(sprite_path.name)
        if not pokemon_id or not sprite_type:
            logger.warning("%s: skipping - unable to parse filename", sprite_path.name)
            continue
        
        # Determine target badge height based on sprite type
        target_badge_height = target_front_badge_height if sprite_type == 'front' else target_back_badge_height

        try:

            result = process_pair(sprite_path, output_dir, logger, badges_dir, weaknesses_data, 
                                 target_badge_height, min_front_height, badge_location, padding_mode, custom_padding,
                                 pre_badge_scale)

            if result:
                # In Shiny Hunter Mode 1 (bullseye_normal), skip adding shiny sprites to results
                # This prevents them from being added to scale override tables
                skip_result = (shiny_hunter_mode == "bullseye_normal" and 
                              is_shiny and 
                              sprite_type == 'front')
                
                if not skip_result:
                    results[sprite_path.name] = result
                else:
                    logger.info("✨ %s: Shiny sprite processed but excluded from scale tables (using Bullseye originals for normals)", sprite_path.name)

        except Exception as exc:  # pylint: disable=broad-except

            logger.exception("%s: failed to process due to %s", sprite_path.name, exc)

    # Save processing summary
    save_processing_summary(results, log_dir, logger)





def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:

    parser = argparse.ArgumentParser(description="Add type weakness badges to Pokémon sprites.")

    parser.add_argument("--sprite-dir", type=Path, default=Path("sprites"), help="Directory containing sprite files")

    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Directory to write processed sprites")

    parser.add_argument("--log-dir", type=Path, default=Path("logs"), help="Directory to write logs and summaries")

    parser.add_argument("--badges-dir", type=Path, default=Path("badges"), help="Directory containing badge images")

    parser.add_argument("--weaknesses-json", type=Path, default=Path("pokemon_weaknesses.json"), help="Path to Pokemon weaknesses JSON file")

    parser.add_argument("--bullseye-dir", type=Path, required=True, help="Directory containing Bullseye sprites (required for fallback)")

    parser.add_argument("--limit", type=int, default=None, help="Optionally limit number of sprites processed")
    
    parser.add_argument("--process-back-sprites", action="store_true", help="Add badges to back sprites (default: False)")
    
    parser.add_argument("--ignore-back-sprites", action="store_true", help="Completely ignore back sprites - don't copy or process them (default: False)")
    
    parser.add_argument("--use-bullseye-fallback", action="store_true", default=True, help="Copy Bullseye sprites as fallback when replacements don't exist (default: True)")
    
    parser.add_argument("--shiny-hunter-mode", type=str, choices=["bullseye_normal", "replacement_normal"], 
                       default=None, help="Shiny Hunter Mode: 'bullseye_normal' = Bullseye normals + Replacement shinies, "
                       "'replacement_normal' = Replacement normals + Bullseye shinies (only affects front sprites)")
    
    parser.add_argument("--badge-height", type=float, default=None, help="Manual override for badge height in pixels (default: auto-calculated as 1/8 of max height, min 15px)")
    
    parser.add_argument("--min-height", type=float, default=None, help="Manual override for minimum front sprite height in pixels (default: 100px or 51%% of max, whichever is greater)")
    
    parser.add_argument("--no-summary-table", action="store_false", dest="create_summary_table", default=True, help="Exclude summary sprites from scale tables (default: create tables)")
    
    parser.add_argument("--no-front-table", action="store_false", dest="create_front_table", default=True, help="Exclude front sprites from scale tables (default: create tables)")
    
    parser.add_argument("--no-back-table", action="store_false", dest="create_back_table", default=True, help="Exclude back sprites from scale tables (default: create tables)")
    
    parser.add_argument("--badge-location", type=str, choices=["left", "right"], default="right",
                       help="Badge location: 'left' = badges on left side, 'right' = badges on right side (default: right)")
    
    parser.add_argument("--padding-mode", type=str, choices=["left", "right", "none"], default="left",
                       help="Sprite centering mode: 'left' = padding on left, "
                            "'right' = padding on right, 'none' = no centering padding (default: left)")
    
    parser.add_argument("--custom-padding", type=int, default=None,
                       help="Custom padding in pixels. If not specified, uses badge width + gap for centering.")
    
    parser.add_argument("--pre-badge-scale", type=float, default=100.0,
                       help="Scale percentage to apply before badges are added (default: 100, no scaling)")

    return parser.parse_args(argv)





def main() -> None:

    args = parse_args()

    run_pipeline(args.sprite_dir, args.output_dir, args.log_dir, args.badges_dir, args.weaknesses_json, 
                args.bullseye_dir, args.limit, args.process_back_sprites, args.shiny_hunter_mode,
                args.badge_height, args.min_height, args.use_bullseye_fallback,
                args.create_summary_table, args.create_front_table, args.create_back_table,
                args.badge_location, args.padding_mode, args.custom_padding, args.ignore_back_sprites,
                args.pre_badge_scale)





if __name__ == "__main__":

    main()







