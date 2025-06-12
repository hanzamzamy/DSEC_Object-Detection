"""
Random Object Placement Animation Generator for Blender

This script animates multiple 3D objects (Oreo cookies) by placing them at random positions 
and orientations within the camera's view for each frame. It ensures all objects remain 
visible to the camera throughout the animation.

The animation creates a diverse dataset of object arrangements with different positions and 
rotations, which is ideal for training object detection models that need to recognize objects
in varied scenes and configurations.

Usage:
    1. Set the object names in the script (default: "oreo_biscuit_1", "oreo_biscuit_2", "oreo_biscuit_3")
    2. Configure animation parameters (frame range, position constraints)
    3. Run the script in Blender to generate keyframes

Configuration:
    object_names: List of object names to animate
    frame_start, frame_end: Animation frame range (default: 1-2000)
    bounds_margin: Margin from edge of frame to keep objects visible (default: 0.1)
    position_range: Range for random positioning of objects (default: 0.45)
    min_cam_distance: Minimum distance objects must be from camera (default: 0.1)
    max_attempts: Maximum placement attempts per object per frame (default: 100)
"""

import bpy
import random
import math
from mathutils import Vector, Quaternion, Euler
import bpy_extras

# === Configuration ===
object_names = ["oreo_biscuit_1", "oreo_biscuit_2", "oreo_biscuit_3"]
camera = bpy.context.scene.camera
frame_start = 1
frame_end = 2000
bounds_margin = 0.1
position_range = 0.45
min_cam_distance = 0.1
max_attempts = 100

# === Initialize Scene and Objects ===
bpy.context.scene.frame_start = frame_start
bpy.context.scene.frame_end = frame_end

objects = []
for name in object_names:
    obj = bpy.data.objects.get(name)
    if obj:
        obj.animation_data_clear()
        obj.rotation_mode = 'QUATERNION'
        objects.append(obj)
    else:
        print(f"Warning: Object '{name}' not found.")

# === Helper: Check if object is visible in camera view ===
def is_object_visible(obj, cam):
    """
    Determines if an object is visible within the camera's view.
    
    This function projects the object's 3D position into the camera's 2D view space and
    checks if it falls within the camera's frame boundaries, accounting for the specified
    margin.
    
    Args:
        obj: Blender object to check for visibility
        cam: Blender camera object defining the view
        
    Returns:
        bool: True if object is visible in camera view (within bounds_margin), False otherwise
        
    Note:
        - Uses bounds_margin to ensure objects aren't too close to the frame edge
        - Checks x and y coordinates are within [margin, 1-margin] range
        - Ensures z coordinate is positive (object is in front of camera)
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    scene = bpy.context.scene
    co_3d = obj_eval.location
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co_3d)
    return (0 + bounds_margin < co_2d.x < 1 - bounds_margin and
            0 + bounds_margin < co_2d.y < 1 - bounds_margin and
            co_2d.z > 0)

def main():
    """
    Main animation logic:

    For each frame in the animation range:
    1. For each object:
    - Generate random positions and orientations until finding one where:
        - Object is within position_range constraint
        - Object is at least min_cam_distance from camera
        - Object is visible in the camera view (checked with is_object_visible)
    - When valid placement is found, insert keyframes for location and rotation
    - If no valid placement is found after max_attempts, print warning

    The result is an animation sequence where all objects are randomly positioned
    but guaranteed to be visible in each frame.
    """
    cam_pos = camera.matrix_world.translation

    for frame in range(frame_start, frame_end + 1):
        for obj in objects:
            placed = False
            attempts = 0

            while not placed and attempts < max_attempts:
                # Generate random position and orientation
                pos = Vector((random.uniform(-position_range, position_range),
                            random.uniform(-position_range, position_range),
                            random.uniform(-position_range, position_range)))

                rot = Euler((random.uniform(0, 2 * math.pi),
                            random.uniform(0, 2 * math.pi),
                            random.uniform(0, 2 * math.pi)), 'XYZ').to_quaternion()

                # Check distance to camera
                if (pos - cam_pos).length < min_cam_distance:
                    attempts += 1
                    continue

                # Apply transform
                obj.location = pos
                obj.rotation_quaternion = rot

                # Check visibility
                if is_object_visible(obj, camera):
                    obj.keyframe_insert(data_path="location", frame=frame)
                    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame)
                    placed = True

                attempts += 1

            if not placed:
                print(f"Frame {frame} | {obj.name}: No valid placement found in {max_attempts} attempts.")

main()