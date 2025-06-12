package org.hanz.oreoar.ar.scene

import com.google.android.filament.Engine
import com.google.ar.core.Coordinates2d
import com.google.ar.core.Frame
import io.github.sceneview.loaders.MaterialLoader
import io.github.sceneview.node.Node
import org.hanz.oreoar.ar.entity.ObjectManager
import org.hanz.oreoar.ml.detector.YOLOObjectDetector

/** Manages the AR scene, including object detection and placement.
 *
 * @property objectDetector The YOLO object detector for detecting objects in the AR scene.
 * @property objectManager The manager for handling AR objects in the scene.
 * @property isProcessingFrame Flag indicating if a frame is currently being processed.
 */
class SceneManager(
    val objectDetector: YOLOObjectDetector?,
    val objectManager: ObjectManager? = null,
    var isProcessingFrame: Boolean = false,
) {
    /** Processes the AR frame for object detection and placement.
     *
     * @param frame The AR frame to process.
     * @param childNodes The list of child nodes in the AR scene.
     * @param engine The Filament engine used for rendering.
     * @param materialLoader The loader for materials used in the AR scene.
     */
    fun processFrameForDetection(
        frame: Frame,
        childNodes: MutableList<Node>,
        engine: Engine,
        materialLoader: MaterialLoader
    ) {
        if (isProcessingFrame || objectDetector == null) return
        isProcessingFrame = true

        try {
            val mediaImage = frame.acquireCameraImage()

            objectDetector.processImage(mediaImage).forEach { detectedObject ->

                val cpuCoordinates = floatArrayOf(detectedObject.center.x, detectedObject.center.y)
                val viewCoordinates = FloatArray(2)

                frame.transformCoordinates2d(
                    Coordinates2d.IMAGE_PIXELS,
                    cpuCoordinates,
                    Coordinates2d.VIEW,
                    viewCoordinates
                )

                // Try to place object at detection position
                objectManager?.placeObject(viewCoordinates[0], viewCoordinates[1], frame, childNodes, engine, materialLoader)
            }

            isProcessingFrame = false
            mediaImage.close()
        } catch (e: Exception) {
            isProcessingFrame = false
        }
    }
}