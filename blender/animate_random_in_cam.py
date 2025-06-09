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
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    scene = bpy.context.scene
    co_3d = obj_eval.location
    co_2d = bpy_extras.object_utils.world_to_camera_view(scene, cam, co_3d)
    return (0 + bounds_margin < co_2d.x < 1 - bounds_margin and
            0 + bounds_margin < co_2d.y < 1 - bounds_margin and
            co_2d.z > 0)

# === Main Animation Loop ===
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
