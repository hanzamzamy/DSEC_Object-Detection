# Oreo Cookie Detector - Android AR Implementation

This Android application implements a real-time Oreo cookie detector using YOLO in an Augmented Reality environment. The app uses the trained TensorFlow Lite model to detect Oreo cookies in the camera feed and places virtual objects at their locations in AR space.



https://github.com/user-attachments/assets/535911ea-dac5-4077-90e6-1b22413c2750



## Features

- **Real-time Oreo Cookie Detection**: Uses YOLOv11 model converted to TFLite format
- **Immersive AR Experience**: Places virtual markers at detected cookie locations
- **Interactive Character**: A 3D avatar that can navigate to detected cookies
- **Modern UI**: Built with Jetpack Compose and Material3

## Technology Stack

- **AR Core**: Google's augmented reality platform
- **SceneView**: Modern AR rendering library with Jetpack Compose support
- **TensorFlow Lite**: Lightweight ML framework for mobile deployment
- **Jetpack Compose**: Modern UI toolkit for Android
- **Material3**: Latest Material Design implementation

## Components

### ML Detection

The cookie detection is implemented in `YOLOObjectDetector.kt`, which:

- Loads the TFLite model (`cookie_v1.tflite`) from assets
- Processes camera frames to detect Oreo cookies
- Implements Non-Maximum Suppression (NMS) to filter overlapping detections
- Provides detection information as `Detection` objects with bounding boxes and confidence scores

### AR Integration

The AR functionality is managed by several components:

1. **SceneManager**: `SceneManager.kt`
   - Bridges the detection system with AR scene
   - Processes frames for detection and places objects in AR space

2. **ObjectManager**: `ObjectManager.kt`
   - Handles AR object placement, selection, and removal
   - Ensures objects are placed correctly in 3D space

3. **AvatarController**: `AvatarController.kt`
   - Controls a 3D character that can navigate to detected cookies
   - Handles animations and movement in the AR environment

### UI Components

The UI is built with Jetpack Compose and Material3:

- **ScreenOverlay**: `ScreenOverlay.kt`
  - Provides control buttons and information text overlay
  - Shows detection status and allows interaction with AR objects

- **Theme**: `Theme.kt`
  - Implements Material3 theming for the application

## How It Works

1. **Detection Pipeline**:
   - Camera frames are processed by the TFLite model
   - Detected cookies are converted to screen coordinates
   - AR hit testing maps 2D coordinates to 3D world positions
   - Virtual markers are placed at these 3D positions

2. **AR Interaction**:
   - Users can tap on detected objects to select them
   - The avatar can be commanded to navigate to selected objects
   - The system handles object selection, placement and removal

3. **User Experience**:
   - Instructional text guides users through the AR experience
   - Control panel provides buttons for common actions
   - Plane visualization helps users understand the AR mapping

## Implementation Highlights

### AR Scene Integration

```kotlin
// In MainActivity.kt
ARScene(
    modifier = Modifier.fillMaxSize(),
    childNodes = childNodes,
    engine = engine,
    view = view,
    modelLoader = modelLoader,
    collisionSystem = collisionSystem,
    sessionConfiguration = { session, config ->
        config.depthMode = when (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
            true -> Config.DepthMode.AUTOMATIC
            else -> Config.DepthMode.DISABLED
        }
        config.instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
        config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
    }
)
```

### Detection and AR Placement

```kotlin
// In SceneManager.kt
fun processFrameForDetection(
    frame: Frame,
    childNodes: MutableList<Node>,
    engine: Engine,
    materialLoader: MaterialLoader
) {
    // Process the current camera frame
    val mediaImage = frame.acquireCameraImage()
    
    // Run object detection
    objectDetector.processImage(mediaImage).forEach { detectedObject ->
        // Transform image coordinates to view coordinates
        frame.transformCoordinates2d(
            Coordinates2d.IMAGE_PIXELS,
            floatArrayOf(detectedObject.center.x, detectedObject.center.y),
            Coordinates2d.VIEW,
            viewCoordinates
        )
        
        // Place an AR object at the detection position
        objectManager?.placeObject(
            viewCoordinates[0], viewCoordinates[1], 
            frame, childNodes, engine, materialLoader
        )
    }
}
```

### Avatar Navigation

```kotlin
// In AvatarController.kt
fun navigateAvatarToObject(targetNode: AnchorNode, margin: Float = 0f) {
    // Find target position
    val targetPosition = targetNode.worldPosition.let { pos ->
        floatArrayOf(pos.x, pos.y, pos.z)
    }
    
    // Create anchor for navigation
    avatarNode.session?.createAnchor(pose)?.let { newAnchor ->
        moveAvatarToLocation(
            newAnchor = newAnchor,
            movementSpeed = movementSpeed,
            rotationSpeed = rotationSpeed,
            smoothMovement = smoothMovement,
            onMoveComplete = {
                // Play reaction animation when reached
                modelNode.playAnimation("react")
                // Return to idle after animation completes
                lifecycleScope.launch {
                    delay((reactAnimDuration * 1000L).toLong())
                    modelNode.stopAnimation("react")
                    modelNode.playAnimation("idle")
                }
            }
        )
    }
}
```

## Getting Started

1. Clone the repository.
2. Open the project in Android Studio.
3. Ensure you have the latest AR Core compatible device. SceneView requirement need higher SDK, but device compatibility remains same.
4. Build and install the app.
5. Move camera to get trackable surface.
6. Summon avatar using button. Optionally, disable plane renderer for immersive experience.
7. Scan Oreo cookie. An indicator will be placed in AR space.
8. Oreo indicator can be selected, moved, and deleted. Use button to interact with avatar / object.
9. Double tap on surface to command avatar to move. Feel free to drag-and-drop.
10. Enjoy.

## Requirements

- Android device with AR Core support. SceneView need min. Android 9 SDK.
- Camera permission
- Stable lighting conditions for optimal detection
