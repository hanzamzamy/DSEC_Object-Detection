package org.hanz.oreoar.ar.entity

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Color
import com.google.android.filament.Engine
import com.google.ar.core.Frame
import io.github.sceneview.ar.arcore.createAnchorOrNull
import io.github.sceneview.ar.arcore.isValid
import io.github.sceneview.ar.node.AnchorNode
import io.github.sceneview.loaders.MaterialLoader
import io.github.sceneview.material.setColor
import io.github.sceneview.node.Node
import io.github.sceneview.node.SphereNode
import io.github.sceneview.math.Position

/** Manages AR objects in the scene, allowing for placement, selection, and removal.
 *
 * @property objectNodes List of currently placed object nodes.
 * @property indicatorSize Size of the indicator sphere for new objects.
 * @property marginSize Margin size to prevent overlapping objects.
 */
class ObjectManager(
    private var indicatorSize: Float = 0.01f,
    val objectNodes: MutableList<AnchorNode> = mutableListOf(),
    var marginSize: Float = 0.03f
) {
    var selectedObjectNode by mutableStateOf<AnchorNode?>(null)

    /** Gets the currently selected object node.
     *
     * @return The selected AnchorNode or null if none is selected.
     */
    fun selectObject(anchorNode: AnchorNode?) {
        // Deselect previous
        selectedObjectNode?.let { previous ->
            (previous.childNodes.firstOrNull() as? SphereNode)?.apply {
                materialInstance.setColor(Color.Yellow.copy(alpha = 0.25f))
            }
        }

        // Select new
        selectedObjectNode = anchorNode

        // Highlight selected object
        anchorNode?.let {
            (it.childNodes.firstOrNull() as? SphereNode)?.apply {
                materialInstance.setColor(Color.Red.copy(alpha = 0.25f))
            }
        }
    }

    /** Checks if an object exists near the specified world position.
     *
     * @param worldPosition The position to check for nearby objects.
     * @return True if an object exists within the margin size, false otherwise.
     */
    private fun objectExistsNear(worldPosition: Position): Boolean {
        return objectNodes.any { anchorNode ->
            // Calculate distance manually using Euclidean distance formula
            val dx = anchorNode.worldPosition.x - worldPosition.x
            val dy = anchorNode.worldPosition.y - worldPosition.y
            val dz = anchorNode.worldPosition.z - worldPosition.z
            val distance = kotlin.math.sqrt(dx*dx + dy*dy + dz*dz)

            distance < marginSize
        }
    }

    /** Removes the currently selected object from the scene.
     *
     * @param childNodes The list of child nodes in the scene.
     */
    fun removeSelectedObject(childNodes: MutableList<Node>) {
        selectedObjectNode?.let {
            childNodes.remove(it)
            objectNodes.remove(it)
            it.destroy()
            selectedObjectNode = null
        }
    }

    /** Places a new object in the scene at the specified screen coordinates.
     *
     * @param x The x coordinate on the screen.
     * @param y The y coordinate on the screen.
     * @param frame The current AR frame to use for hit testing.
     * @param childNodes The list of child nodes in the scene.
     * @param engine The Filament engine instance.
     * @param materialLoader The MaterialLoader to create material instances.
     */
    fun placeObject(
        x: Float, y: Float,
        frame: Frame,
        childNodes: MutableList<Node>,
        engine: Engine,
        materialLoader: MaterialLoader
    ) {
        // Use hitTest to find a 3D point that corresponds to the 2D detection
        frame.hitTest(x, y).firstOrNull {
            it.isValid(depthPoint = false, point = false)
        }?.createAnchorOrNull()?.let { anchor ->
            // Check if there's already an object near this position to avoid duplication
            val hitPose = anchor.pose
            val worldPosition = io.github.sceneview.math.Position(
                hitPose.tx(),
                hitPose.ty(),
                hitPose.tz()
            )

            if (!objectExistsNear(worldPosition)) {
                // No nearby object, safe to create a new one
                val anchorNode = AnchorNode(engine = engine, anchor = anchor).apply { isEditable = false }

                val sphereNode = SphereNode(
                    engine = engine,
                    radius = indicatorSize,
                    center = io.github.sceneview.math.Position(0f, 0f, 0f),
                    materialInstance = materialLoader.createColorInstance(Color.Green.copy(alpha = 0.7f))
                ).apply { isEditable = false }

                anchorNode.addChildNode(sphereNode)
                childNodes.add(anchorNode)
                objectNodes.add(anchorNode)

                // Select the newly created object
                selectObject(anchorNode)
            }
        }
    }
}