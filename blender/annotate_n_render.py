import bpy
import bpy_extras.object_utils
import mathutils
import os
import random
import math

def compose_setname():
    fn = ""

    if ENABLE_RANDOM_BACKGROUND:
        fn = fn + f"{BACKGROUND_PATTERN}_"

    if ENABLE_RANDOM_LIGHTING:
        fn = fn + f"KIRAKIRA_{NUM_LIGHTS}_{ORBIT_DISTANCE}_"

    if HIDE_SUN:
        fn = fn + f"NOSUN_"

    fn = fn + f"BLUR_{GAUSSIAN_BLUR[0]}_{GAUSSIAN_BLUR[1]}"

    return fn

# Ensure output directories exist
def ensure_directories():
    if ENABLE_RENDER:
        os.makedirs(f"render_result/{SETNAME}", exist_ok=True)

    if ENABLE_ANNOTATION:
        os.makedirs(f"annotation/{SETNAME}/label_vertice", exist_ok=True)

def clean_lights(num_lights):
    for i in range(num_lights):
        bpy.data.objects.remove(bpy.data.objects[f'hikari_{i}'])

# Create multiple lights for random lighting
def create_lights(num_lights):
    lights = []
    for i in range(num_lights):
        light_data = bpy.data.lights.new(name=f"hikari_{i}", type='POINT')
        light_object = bpy.data.objects.new(name=f"hikari_{i}", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        lights.append(light_object)
    return lights

# Animate lights to orbit and set random properties
def animate_lights(scene, lights, objects, start_frame, end_frame, orbit_distance):
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

# Generate grid pattern background
def generate_grid_pattern(background_node, mapping_node, checker_node, frame):
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

# Generate noise pattern background
def generate_noise_pattern(background_node, mapping_node, noise_node, frame):
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

# Generate noise pattern background
def generate_voronoi_pattern(background_node, mapping_node, voronoi_node, frame):
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

# Generate solid color background
def generate_solid_pattern(background_node, frame):
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

# Perform annotation for a single frame
def annotate_frame(scene, frame):
    scene.frame_set(frame)

    label_filepath = {
        'vertice_bbox': f"annotation/{SETNAME}/label_vertice/{frame+FRAME_OFFSET}.txt",
    }

    camera = bpy.data.objects['Camera']

    for obj in bpy.data.objects:
        if obj.name.startswith(tuple(classification.keys())):
            create_data(camera, scene, obj, label_filepath)

# Create annotation data
def create_data(camera, scene, obj, label_save):
    '''
    Dataset format:
    <class> <cx> <cy> <w> <h>

    <class>   Object class index: An integer representing the class of the object.
    <cx> <cy> Object center coordinates: The x and y coordinates of the center of the object, normalized to be between 0 and 1.
    <w> <h>   Object width and height: The width and height of the object, normalized to be between 0 and 1.
    '''
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

# Set up etc
def render_setup():
     sun_object = bpy.data.objects.get('Sun')
     sun_object.hide_render = HIDE_SUN

# Render a single frame
def render_frame(scene, frame):
    scene.frame_set(frame)
    scene.render.filepath = f"render_result/{SETNAME}/{frame+FRAME_OFFSET}.jpg"
    bpy.ops.render.render(write_still=True)

# Main function to process all frames
def process_frames():
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
