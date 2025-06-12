"""
Fibonacci Sphere Animation Generator for Blender

This script animates a 3D object (Oreo cookie) by rotating it through multiple viewing angles 
systematically distributed on a sphere. It uses a Fibonacci sphere distribution algorithm
to ensure even coverage of all possible orientations, combined with rotational spin at each position.

The animation creates a comprehensive dataset of the object viewed from all possible angles,
which is ideal for training object detection models that need to recognize the object
regardless of orientation.

Usage:
    1. Set the object name in the script (default: "oreo_biscuit")
    2. Configure n_pitch (points on sphere) and n_spin (rotations per position)
    3. Run the script in Blender to generate keyframes

Configuration:
    n_pitch: Number of points sampled on the sphere (default: 100)
    n_spin: Number of rotational positions at each point (default: 20)
    total_frames: Total animation frames (n_pitch * n_spin)
"""

import bpy
import math
from mathutils import Vector, Quaternion

# Settings
obj = bpy.data.objects["oreo_biscuit"]
obj.animation_data_clear()
obj.rotation_mode = 'QUATERNION'

# Output settings
n_pitch = 100  # Points on the sphere
n_spin = 20    # Spins per orientation
total_frames = n_pitch * n_spin
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = total_frames

frame = 0

def fibonacci_sphere(samples):
    """
    Generates points evenly distributed on a unit sphere using the Fibonacci spiral method.
    
    This algorithm creates a relatively uniform distribution of points on a sphere
    by using the golden angle to determine point placement. It's more efficient and 
    provides better coverage than random sampling.
    
    Args:
        samples (int): The number of points to generate on the sphere
        
    Returns:
        list: A list of Vector objects representing 3D points on a unit sphere
        
    Note:
        The algorithm is based on the golden angle (phi) which provides optimal spacing
        between points on a sphere.
    """
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

def main():
    """
    Executes the rotation animation logic:

    1. Gets points distributed evenly on a sphere using fibonacci_sphere()
    2. For each point (direction vector):
    - Computes a base quaternion rotation that points the object in that direction
    - For each spin position:
        - Applies additional rotation around the direction vector
        - Combines rotations and creates a keyframe
        - Increments the frame counter

    The result is a sequence of keyframes that show the object from every possible viewpoint,
    with a total of n_pitch * n_spin unique orientations.
    """
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

main()
