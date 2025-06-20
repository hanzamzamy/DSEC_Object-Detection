'''
Synthetic Data Generator for Oreo Cookie Detection

This Blender script generates synthetic training data for object detection models by
rendering 3D models of Oreo cookies with various backgrounds, lighting conditions,
and positions while automatically creating accurate YOLO format annotations.

Usage:
    1. Import the script into Blender
    2. Configure the parameters below to control the data generation process
    3. Run the script to generate images and annotation files

Configuration:
    SETNAME: Name prefix for the dataset (default: 'test')
    WIDTH, HEIGHT: Rendering resolution (default: 640x640)
    ENABLE_ANNOTATION: Whether to generate annotation files (default: False)
    ENABLE_RENDER: Whether to render images (default: True)
    ENABLE_RANDOM_BACKGROUND: Whether to generate random backgrounds (default: True)
    ENABLE_RANDOM_LIGHTING: Whether to generate random lighting (default: True)
    BACKGROUND_PATTERN: Type of background pattern (options: 'GRID', 'NOISE', 'VORONOI', 'SOLID')
    NUM_LIGHTS: Number of random lights to create (default: 5)
    ORBIT_DISTANCE: Distance for orbiting lights (default: 1.0)
    HIDE_SUN: Whether to hide the default sun light (default: False)
    FRAME_OFFSET: Offset for frame numbering (default: 0)

Functions:
    - compose_setname(): Generates dataset name based on parameters
    - ensure_directories(): Creates output directories
    - clean_lights(): Removes generated lights
    - create_lights(): Creates random lights
    - animate_lights(): Animates lights with random properties
    - generate_*_pattern(): Creates various background patterns
    - animate_background(): Sets up and animates backgrounds
    - annotate_frame(): Creates annotations for a single frame
    - create_data(): Converts 3D object coordinates to 2D bounding boxes
    - render_setup(): Sets up rendering environment
    - render_frame(): Renders a single frame
    - process_frames(): Main function to process all frames

Output Format:
    - Images: JPG files in render_result/{SETNAME}/
    - Annotations: YOLO format text files in annotation/{SETNAME}/label_vertice/
      Format: <class> <cx> <cy> <w> <h>
      Where:
        - class: Object class index (0 for Oreo cookie)
        - cx, cy: Object center coordinates (normalized 0-1)
        - w, h: Object width and height (normalized 0-1)

Example:
    To generate a dataset with different background patterns:
    ```
    for bgpatt_opt in ['SOLID', 'NOISE', 'VORONOI']:
        BACKGROUND_PATTERN = bgpatt_opt
        SETNAME = compose_setname()
        process_frames()
    ```
'''

import bpy
import bpy_extras.object_utils
import mathutils
import os
import random
import math

def compose_setname():
    """
    Generates a dataset name based on the current configuration settings.
    
    The name includes information about the background pattern, lighting settings,
    sun visibility, and blur settings to help identify dataset characteristics.
    
    Returns:
        str: A formatted string representing the dataset name
    """
    fn = ""

    if ENABLE_RANDOM_BACKGROUND:
        fn = fn + f"{BACKGROUND_PATTERN}_"

    if ENABLE_RANDOM_LIGHTING:
        fn = fn + f"KIRAKIRA_{NUM_LIGHTS}_{ORBIT_DISTANCE}_"

    if HIDE_SUN:
        fn = fn + f"NOSUN_"

    fn = fn + f"BLUR_{GAUSSIAN_BLUR[0]}_{GAUSSIAN_BLUR[1]}"

    return fn

def ensure_directories():
    """
    Creates necessary output directories for rendered images and annotations.
    
    If ENABLE_RENDER is True, creates the render_result/{SETNAME} directory.
    If ENABLE_ANNOTATION is True, creates the annotation/{SETNAME}/label_vertice directory.
    
    All directories are created with exist_ok=True to prevent errors if they already exist.
    """
    if ENABLE_RENDER:
        os.makedirs(f"render_result/{SETNAME}", exist_ok=True)

    if ENABLE_ANNOTATION:
        os.makedirs(f"annotation/{SETNAME}/label_vertice", exist_ok=True)

def clean_lights(num_lights):
    """
    Removes all previously created lights from the scene.
    
    Args:
        num_lights (int): Number of lights to remove
        
    Note:
        Lights are assumed to be named 'hikari_0', 'hikari_1', etc.
    """
    for i in range(num_lights):
        bpy.data.objects.remove(bpy.data.objects[f'hikari_{i}'])

def create_lights(num_lights):
    """
    Creates multiple point lights for random lighting in the scene.
    
    Args:
        num_lights (int): Number of lights to create
        
    Returns:
        list: List of light objects created
        
    Note:
        Created lights are named 'hikari_0', 'hikari_1', etc.
    """
    lights = []
    for i in range(num_lights):
        light_data = bpy.data.lights.new(name=f"hikari_{i}", type='POINT')
        light_object = bpy.data.objects.new(name=f"hikari_{i}", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        lights.append(light_object)
    return lights

def animate_lights(scene, lights, objects, start_frame, end_frame, orbit_distance):
    """
    Animates light objects with random properties throughout the animation frames.
    
    For each frame, each light is:
    - Positioned randomly around a reference object
    - Given random color values
    - Given random energy (intensity) values
    - Keyframed for location, color and energy
    
    Args:
        scene: Blender scene object
        lights (list): List of light objects to animate
        objects (list): List of reference objects to orbit around
        start_frame (int): First frame of animation
        end_frame (int): Last frame of animation
        orbit_distance (float): Radius for light orbiting around reference objects
    """
    for light in lights:
        for frame in range(start_frame, end_frame + 1):
            scene.frame_set(frame)

            ref_object = random.choice(objects)
            ref_location = ref_object.location

            angle_x = random.uniform(0, 2 * math.pi)
            angle_y = random.uniform(0, 2 * math.pi)

            x_offset = orbit_distance * math.sin(angle_x) * math.cos(angle_y)
            y_offset = orbit_distance * math.sin(angle_x) * math.sin(angle_y)
            z_offset = orbit_distance * math.cos(angle_x)

            light.location = (
                ref_location.x + x_offset,
                ref_location.y + y_offset,
                ref_location.z + z_offset
            )

            light.data.color = (
                random.uniform(0.0, 1.0),
                random.uniform(0.0, 1.0),
                random.uniform(0.0, 1.0)
            )

            light.data.energy = random.uniform(10.0, 50.0)
            light.keyframe_insert(data_path="location", frame=frame)
            light.data.keyframe_insert(data_path="color", frame=frame)
            light.data.keyframe_insert(data_path="energy", frame=frame)

def generate_grid_pattern(background_node, mapping_node, checker_node, frame):
    """
    Generates a checker grid pattern background with random properties for the given frame.
    
    Randomizes and keyframes:
    - Checker scale
    - Checker colors (two random colors)
    - Transformation (rotation, location, scale)
    
    Args:
        background_node: Blender background shader node
        mapping_node: Blender mapping node for transformation
        checker_node: Blender checker texture node
        frame (int): Current frame number to set keyframes
    """
    # Randomize checker scale
    checker_node.inputs['Scale'].default_value = random.uniform(10.0, 50.0)

    # Randomize checker colors
    checker_node.inputs['Color1'].default_value = (
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        1.0
    )
    checker_node.inputs['Color2'].default_value = (
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        1.0
    )

    # Randomize transformation
    mapping_node.inputs['Rotation'].default_value = (
        random.uniform(0, math.pi),
        random.uniform(0, math.pi),
        random.uniform(0, math.pi)
    )
    mapping_node.inputs['Location'].default_value = (
        random.uniform(-5.0, 5.0),
        random.uniform(-5.0, 5.0),
        0.0
    )
    mapping_node.inputs['Scale'].default_value = (
        random.uniform(0.5, 2.0),
        random.uniform(0.5, 2.0),
        1.0
    )

    # Keyframe parameters
    checker_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)
    checker_node.inputs['Color1'].keyframe_insert(data_path="default_value", frame=frame)
    checker_node.inputs['Color2'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Rotation'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Location'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)

    background_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame)

def generate_noise_pattern(background_node, mapping_node, noise_node, frame):
    """
    Generates a noise pattern background with random properties for the given frame.
    
    Randomizes and keyframes:
    - Noise scale, detail, roughness, distortion, and lacunarity
    - Transformation (rotation, location, scale)
    
    Args:
        background_node: Blender background shader node
        mapping_node: Blender mapping node for transformation
        noise_node: Blender noise texture node
        frame (int): Current frame number to set keyframes
    """
    # Randomize noise
    noise_node.inputs['Scale'].default_value = random.uniform(1.0, 10.0)
    noise_node.inputs['Detail'].default_value = random.uniform(0.0, 16.0)
    noise_node.inputs['Roughness'].default_value = random.uniform(0.0, 0.1)
    noise_node.inputs['Distortion'].default_value = random.uniform(0.0, 0.5)
    noise_node.inputs['Lacunarity'].default_value = random.uniform(8.0, 32.0)

    mapping_node.inputs['Rotation'].default_value = (
        random.uniform(0, math.pi),
        random.uniform(0, math.pi),
        random.uniform(0, math.pi)
    )
    mapping_node.inputs['Location'].default_value = (
        random.uniform(-5.0, 5.0),
        random.uniform(-5.0, 5.0),
        0.0
    )
    mapping_node.inputs['Scale'].default_value = (
        random.uniform(0.5, 2.0),
        random.uniform(0.5, 2.0),
        1.0
    )

    # Keyframe parameters
    noise_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)
    noise_node.inputs['Detail'].keyframe_insert(data_path="default_value", frame=frame)
    noise_node.inputs['Roughness'].keyframe_insert(data_path="default_value", frame=frame)
    noise_node.inputs['Distortion'].keyframe_insert(data_path="default_value", frame=frame)
    noise_node.inputs['Lacunarity'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Rotation'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Location'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)

    background_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame)

def generate_voronoi_pattern(background_node, mapping_node, voronoi_node, frame):
    """
    Generates a Voronoi pattern background with random properties for the given frame.
    
    Randomizes and keyframes:
    - Voronoi scale, detail, roughness, randomness, and lacunarity
    - Transformation (rotation, location, scale)
    
    Args:
        background_node: Blender background shader node
        mapping_node: Blender mapping node for transformation
        voronoi_node: Blender Voronoi texture node
        frame (int): Current frame number to set keyframes
    """
    # Randomize noise
    voronoi_node.inputs['Scale'].default_value = random.uniform(1.0, 10.0)
    voronoi_node.inputs['Detail'].default_value = random.uniform(0.0, 16.0)
    voronoi_node.inputs['Roughness'].default_value = random.uniform(0.0, 0.1)
    voronoi_node.inputs['Randomness'].default_value = random.uniform(0.0, 1.0)
    voronoi_node.inputs['Lacunarity'].default_value = random.uniform(8.0, 32.0)

    mapping_node.inputs['Rotation'].default_value = (
        random.uniform(0, math.pi),
        random.uniform(0, math.pi),
        random.uniform(0, math.pi)
    )
    mapping_node.inputs['Location'].default_value = (
        random.uniform(-5.0, 5.0),
        random.uniform(-5.0, 5.0),
        0.0
    )
    mapping_node.inputs['Scale'].default_value = (
        random.uniform(0.5, 2.0),
        random.uniform(0.5, 2.0),
        1.0
    )

    # Keyframe parameters
    voronoi_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)
    voronoi_node.inputs['Detail'].keyframe_insert(data_path="default_value", frame=frame)
    voronoi_node.inputs['Roughness'].keyframe_insert(data_path="default_value", frame=frame)
    voronoi_node.inputs['Randomness'].keyframe_insert(data_path="default_value", frame=frame)
    voronoi_node.inputs['Lacunarity'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Rotation'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Location'].keyframe_insert(data_path="default_value", frame=frame)
    mapping_node.inputs['Scale'].keyframe_insert(data_path="default_value", frame=frame)

    background_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame)

def generate_solid_pattern(background_node, frame):
    """
    Generates a solid color background with random RGB values for the given frame.
    
    Args:
        background_node: Blender background shader node
        frame (int): Current frame number to set keyframes
    """
    # Set random solid color
    background_node.inputs[0].default_value = (
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        random.uniform(0.0, 1.0),
        1.0
    )

    # Keyframe color
    background_node.inputs[0].keyframe_insert(data_path="default_value", frame=frame)

# Animate random background
def animate_background(scene, start_frame, end_frame):
    """
    Sets up and animates the background for all frames based on BACKGROUND_PATTERN.
    
    Creates necessary nodes for the selected pattern type and applies the appropriate
    pattern generation function to each frame.
    
    Args:
        scene: Blender scene object
        start_frame (int): First frame of animation
        end_frame (int): Last frame of animation
    """
    world = bpy.data.worlds["World"]
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    for node in nodes:
        if node.type in ['TEX_CHECKER', 'TEX_NOISE', 'TEX_VORONOI', 'MAPPING', 'TEX_COORD']:
            nodes.remove(node)

    background_node = nodes.get("Background")

    if BACKGROUND_PATTERN != 'SOLID':
        mapping_node = nodes.new(type='ShaderNodeMapping')
        tex_coord_node = nodes.new(type='ShaderNodeTexCoord')

        if BACKGROUND_PATTERN == 'GRID':
            pattern_node = nodes.new(type='ShaderNodeTexChecker')
        elif BACKGROUND_PATTERN == 'NOISE':
            pattern_node = nodes.new(type='ShaderNodeTexNoise')
        elif BACKGROUND_PATTERN == 'VORONOI':
            pattern_node = nodes.new(type='ShaderNodeTexVoronoi')

        links.new(tex_coord_node.outputs['Generated'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], pattern_node.inputs['Vector'])
        links.new(pattern_node.outputs['Color'], background_node.inputs[0])

    for frame in range(start_frame, end_frame + 1):
        if BACKGROUND_PATTERN == 'GRID':
            generate_grid_pattern(background_node, mapping_node, pattern_node, frame)
        elif BACKGROUND_PATTERN == 'NOISE':
            generate_noise_pattern(background_node, mapping_node, pattern_node, frame)
        elif BACKGROUND_PATTERN == 'SOLID':
            generate_solid_pattern(background_node, frame)
        elif BACKGROUND_PATTERN == 'VORONOI':
            generate_voronoi_pattern(background_node, mapping_node, pattern_node, frame)

def annotate_frame(scene, frame):
    """
    Creates annotation files for objects in the given frame.
    
    Processes each object that starts with a name defined in the classification dictionary
    and creates YOLO format bounding box annotations.
    
    Args:
        scene: Blender scene object
        frame (int): Frame number to annotate
    """
    scene.frame_set(frame)

    label_filepath = {
        'vertice_bbox': f"annotation/{SETNAME}/label_vertice/{frame+FRAME_OFFSET}.txt",
    }

    camera = bpy.data.objects['Camera']

    for obj in bpy.data.objects:
        if obj.name.startswith(tuple(classification.keys())):
            create_data(camera, scene, obj, label_filepath)

def create_data(camera, scene, obj, label_save):
    """
    Converts 3D object data to 2D bounding box annotations in YOLO format.
    
    Calculates the bounding box by projecting the object's vertices into camera space.
    Writes annotation in format: <class> <cx> <cy> <w> <h>
    
    Args:
        camera: Blender camera object
        scene: Blender scene object
        obj: Blender object to annotate
        label_save (dict): Dictionary with paths for saving labels
        
    Note:
        Skips objects that are not visible in the camera view
        Format: <class_idx> <center_x> <center_y> <width> <height>
        - All values are normalized between 0 and 1
        - The Y-axis is inverted for compatibility with computer vision conventions
    """
    matrix = obj.matrix_world
    mesh = obj.data

    # Get 2D bbox from vertices
    minX, maxX, minY, maxY = 1, 0, 1, 0
    for vertex in mesh.vertices:
        co = vertex.co
        pos = bpy_extras.object_utils.world_to_camera_view(scene, camera, matrix @ co)
        minX, maxX = min(minX, pos.x), max(maxX, pos.x)
        minY, maxY = min(minY, pos.y), max(maxY, pos.y)

    x_center_v = (minX + maxX) / 2
    y_center_v = 1 - (minY + maxY) / 2  # Invert Y-axis
    width_v, height_v = maxX - minX, maxY - minY

    # Sanity check: Object inside camera view
    if not (0 < x_center_v < 1 and 0 < y_center_v < 1):
        return  # Simply do nothing (there is nothing to add)

    # Determine classification based on prefix
    class_label = -1
    for key in classification:
        if obj.name.startswith(key):
            class_label = classification[key]
            break

    # Write result
    if class_label != -1:
        with open(label_save['vertice_bbox'], 'a') as f:
            f.write(f"{class_label} {x_center_v} {y_center_v} {width_v} {height_v} ")

            f.write("\n")

def render_setup():
    """
    Configures the render settings before rendering.
    
    Currently handles:
    - Setting the sun's visibility based on the HIDE_SUN parameter
    """
    sun_object = bpy.data.objects.get('Sun')
    sun_object.hide_render = HIDE_SUN

def render_frame(scene, frame):
    """
    Renders a single frame and saves it to the output directory.
    
    Args:
        scene: Blender scene object
        frame (int): Frame number to render
    """
    scene.frame_set(frame)
    scene.render.filepath = f"render_result/{SETNAME}/{frame+FRAME_OFFSET}.jpg"
    bpy.ops.render.render(write_still=True)

def process_frames():
    """
    Main function to process all frames in the animation range.
    
    Performs the following operations:
    1. Creates necessary output directories
    2. Annotates frames if ENABLE_ANNOTATION is True
    3. Sets up random lighting if ENABLE_RANDOM_LIGHTING is True
    4. Sets up random backgrounds if ENABLE_RANDOM_BACKGROUND is True
    5. Renders each frame if ENABLE_RENDER is True
    6. Cleans up temporary objects when done
    """
    scene = bpy.context.scene
    start_frame = scene.frame_start
    end_frame = scene.frame_end

    ensure_directories()

    if ENABLE_ANNOTATION:
        for frame in range(start_frame, end_frame + 1):
            annotate_frame(scene, frame)

    if ENABLE_RENDER:
        if ENABLE_RANDOM_LIGHTING:
            lights = create_lights(NUM_LIGHTS)
            animate_lights(scene, lights, [obj for obj in bpy.data.objects if obj.name.startswith(tuple(classification.keys()))], start_frame, end_frame, ORBIT_DISTANCE)

        if ENABLE_RANDOM_BACKGROUND:
            animate_background(scene, start_frame, end_frame)

        for frame in range(start_frame, end_frame + 1):
            render_frame(scene, frame)

        if ENABLE_RANDOM_LIGHTING:
            clean_lights(NUM_LIGHTS)

# Configuration options
SETNAME = 'test'
WIDTH = 640
HEIGHT = 640
ENABLE_ANNOTATION = False
ENABLE_RENDER = True
ENABLE_RANDOM_BACKGROUND = True
ENABLE_RANDOM_LIGHTING = True
BACKGROUND_PATTERN = 'VORONOI' # 'GRID', 'NOISE', 'VORONOI', 'SOLID'
NUM_LIGHTS = 5  # Number of lights for random lighting
ORBIT_DISTANCE = 1.0  # Distance for orbiting lights
HIDE_SUN = False
FRAME_OFFSET = 0

# Classification mapping
classification = {'oreo_biscuit': 0}

# Execute the script
#process_frames()
for bgpatt_opt in ['SOLID', 'NOISE', 'VORONOI']:
    BACKGROUND_PATTERN = bgpatt_opt
    SETNAME = compose_setname()
    process_frames()
