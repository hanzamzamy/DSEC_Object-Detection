import bpy
import math
from mathutils import Vector, Quaternion

# Settings
obj = bpy.data.objects["oreo_biscuit"]
obj.animation_data_clear()
obj.rotation_mode = 'QUATERNION'

# Output settings
n_pitch = 100  # Points on the sphere
n_spin = 40    # Spins per orientation
total_frames = n_pitch * n_spin
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = total_frames

frame = 1

# Fibonacci Sphere sampling
def fibonacci_sphere(samples):
    points = []
    phi = math.pi * (3. - math.sqrt(5.))  # golden angle
    for i in range(samples):
        y = 1 - (i / float(samples - 1)) * 2  # y from 1 to -1
        radius = math.sqrt(1 - y * y)
        theta = phi * i
        x = math.cos(theta) * radius
        z = math.sin(theta) * radius
        points.append(Vector((x, y, z)))
    return points

# Main loop: sample sphere and apply spin
directions = fibonacci_sphere(n_pitch)

for dir_vec in directions:
    # Compute rotation that maps (0, 0, 1) to dir_vec
    up = Vector((0, 0, 1))
    if dir_vec == up:
        base_quat = Quaternion()
    else:
        axis = up.cross(dir_vec)
        angle = up.angle(dir_vec)
        base_quat = Quaternion(axis, angle)

    for i in range(n_spin):
        spin_angle = 2 * math.pi * i / n_spin
        spin_quat = Quaternion(dir_vec, spin_angle)
        final_quat = spin_quat @ base_quat
        obj.rotation_quaternion = final_quat
        obj.keyframe_insert(data_path="rotation_quaternion", frame=frame)
        frame += 1
