package org.hanz.oreoar.ar.entity

import android.content.res.Resources
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.LifecycleCoroutineScope
import com.google.android.filament.Engine
import com.google.ar.core.Anchor
import com.google.ar.core.Frame
import io.github.sceneview.ar.arcore.createAnchorOrNull
import io.github.sceneview.ar.arcore.isValid
import io.github.sceneview.ar.node.AnchorNode
import io.github.sceneview.ar.scene.destroy
import io.github.sceneview.loaders.ModelLoader
import io.github.sceneview.model.getAnimationIndex
import io.github.sceneview.node.ModelNode
import io.github.sceneview.node.Node
import io.github.sceneview.math.Position
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.pow

/** * AvatarController is responsible for managing the avatar's position and movement in an AR environment.
 * It handles avatar placement, movement to new locations, and animations.
 *
 * @property resources The Android resources used for display metrics.
 * @property lifecycleScope The lifecycle scope for managing coroutines.
 * @property avatarModelFile The file path of the avatar model to be loaded.
 * @property currentAnchorNode The current anchor node where the avatar is placed.
 * @property movementJob The job managing the current movement coroutine.
 */
class AvatarController(
    private val resources: Resources,
    private val lifecycleScope: LifecycleCoroutineScope,
    private val avatarModelFile: String,
    private val defaultMovementSpeed: Float = 0.05f,
    private val defaultRotationSpeed: Float = 360f,
    private val defaultSmoothMovement: Boolean = true,
    private var movementJob: kotlinx.coroutines.Job? = null,
    var currentAnchorNode: AnchorNode? = null,
) {
    var isAvatarWalking by mutableStateOf(false)

    /**
     * Moves the avatar to a new location defined by the provided anchor.
     *
     * @param newAnchor The anchor representing the new location.
     * @param movementSpeed The speed of the avatar's movement in units per second.
     * @param rotationSpeed The speed of the avatar's rotation in degrees per second.
     * @param smoothMovement Whether to apply smooth transitions for movement and rotation.
     * @param onMoveComplete Callback invoked when the movement is complete.
     */
    fun moveAvatarToLocation(
        newAnchor: Anchor,
        onMoveComplete: () -> Unit = {isAvatarWalking = false},
        movementSpeed: Float = defaultMovementSpeed,
        rotationSpeed: Float = defaultRotationSpeed,
        smoothMovement: Boolean = defaultSmoothMovement
    ) {
        // Cancel any existing movement
        movementJob?.cancel()

        currentAnchorNode?.let { anchorNode ->
            // Get the model node (avatar)
            val modelNode = anchorNode.childNodes.firstOrNull() as? ModelNode ?: run {
                onMoveComplete()
                return
            }

            // Start walking animation
            modelNode.stopAnimation(modelNode.playingAnimations.keys.firstOrNull() ?: run {
                onMoveComplete()
                return
            })
            modelNode.playAnimation("walk")

            // Get positions and calculate movement parameters
            val startPosition = anchorNode.worldPosition
            val targetPosition = newAnchor.pose.translation
            val startRotation = anchorNode.worldRotation.y

            modelNode.worldPosition = anchorNode.worldPosition
            modelNode.worldRotation = anchorNode.worldRotation

            // Direction vector
            val directionX = targetPosition[0] - startPosition.x
            val directionZ = targetPosition[2] - startPosition.z

            // Distance and timing calculations
            val distance = kotlin.math.sqrt(
                directionX.pow(2) +
                        (targetPosition[1] - startPosition.y).pow(2) +
                        directionZ.pow(2)
            )

            // Calculate target angle and rotation difference
            val targetAngle = Math.toDegrees(kotlin.math.atan2(directionX, directionZ).toDouble()).toFloat()
            var rotationDiff = ((targetAngle - startRotation + 180) % 360) - 180
            if (rotationDiff < -180) rotationDiff += 360

            // Fixed movement durations with reasonable limits
            val movementDuration = ((distance / movementSpeed) * 1000).toLong().coerceIn(100, 5000)
            val rotationDuration = ((abs(rotationDiff) / rotationSpeed) * 1000).toLong().coerceIn(100, 1000)

            movementJob = lifecycleScope.launch {
                try {
                    // ROTATION PHASE
                    if (smoothMovement && abs(rotationDiff) > 1f) {
                        val rotationStartTime = System.currentTimeMillis()
                        while (true) {
                            val progress = ((System.currentTimeMillis() - rotationStartTime).toFloat() / rotationDuration).coerceIn(0f, 1f)
                            if (progress >= 1f) break

                            val currentRotation = startRotation + (rotationDiff * progress)
                            modelNode.worldRotation = io.github.sceneview.math.Rotation(0f, currentRotation, 0f)
                            delay(16)
                        }
                        // Ensure final rotation is exact
                        modelNode.worldRotation = io.github.sceneview.math.Rotation(0f, startRotation + rotationDiff, 0f)
                    } else {
                        // Instant rotation
                        modelNode.worldRotation = io.github.sceneview.math.Rotation(0f, targetAngle, 0f)
                    }

                    // MOVEMENT PHASE
                    if (distance > 0.01f) {
                        val startTime = System.currentTimeMillis()
                        while (true) {
                            val progress = ((System.currentTimeMillis() - startTime).toFloat() / movementDuration).coerceIn(0f, 1f)
                            if (progress >= 1f) break

                            // Simple linear interpolation of position
                            val currentX = startPosition.x + (progress * directionX)
                            val currentY = startPosition.y + (progress * (targetPosition[1] - startPosition.y))
                            val currentZ = startPosition.z + (progress * directionZ)

                            modelNode.worldPosition = io.github.sceneview.math.Position(currentX, currentY, currentZ)
                            delay(16)
                        }
                        // Ensure final position is exact
                        modelNode.worldPosition = io.github.sceneview.math.Position(
                            startPosition.x + directionX,
                            startPosition.y + (targetPosition[1] - startPosition.y),
                            startPosition.z + directionZ
                        )
                    }

                    // Update anchor and finish
                    val oldAnchor = anchorNode.anchor
                    anchorNode.anchor = newAnchor

                    modelNode.position = io.github.sceneview.math.Position(0f, 0f, 0f)

                    oldAnchor.detach()
                    oldAnchor.destroy()

                    modelNode.stopAnimation("walk")
                    modelNode.playAnimation("idle")

                } catch (_: Exception) {
                    // Emergency recovery
                    modelNode.stopAnimation("walk")
                    modelNode.playAnimation("idle")
                } finally {
                    movementJob = null
                    onMoveComplete()
                }
            }
        } ?: onMoveComplete()
    }

    /**
     * Navigates the avatar to a specified object, ensuring it maintains a safe distance.
     *
     * @param selectedNode The anchor node of the object to navigate to.
     * @param safeDistance The minimum distance to maintain from the object.
     * @param movementSpeed The speed of the avatar's movement in units per second.
     * @param rotationSpeed The speed of the avatar's rotation in degrees per second.
     * @param smoothMovement Whether to apply smooth transitions for movement and rotation.
     */
    fun navigateAvatarToObject(
        selectedNode: AnchorNode,
        safeDistance: Float,
        movementSpeed: Float = defaultMovementSpeed,
        rotationSpeed: Float = defaultRotationSpeed,
        smoothMovement: Boolean = defaultSmoothMovement
    ) {
        currentAnchorNode?.let { avatarNode ->
            selectedNode.anchor.let { targetAnchor ->
                // Calculate direction vector
                val avatarPos = avatarNode.worldPosition
                val objectPos = Position(
                    targetAnchor.pose.translation[0],
                    targetAnchor.pose.translation[1],
                    targetAnchor.pose.translation[2]
                )

                // Calculate distance between avatar and object
                val dirX = objectPos.x - avatarPos.x
                val dirY = objectPos.y - avatarPos.y
                val dirZ = objectPos.z - avatarPos.z
                val distance = kotlin.math.sqrt(dirX * dirX + dirY * dirY + dirZ * dirZ)

                val ratio = if (distance > safeDistance) (distance - safeDistance) / distance else 0f

                // Calculate new position
                val newX = avatarPos.x + dirX * ratio
                val newY = avatarPos.y + dirY * ratio
                val newZ = avatarPos.z + dirZ * ratio

                val pose = com.google.ar.core.Pose(
                    floatArrayOf(newX, newY, newZ),
                    targetAnchor.pose.rotationQuaternion
                )

                // Create new anchor and move avatar to it
                avatarNode.session?.createAnchor(pose)?.let { newAnchor ->
                    moveAvatarToLocation(
                        newAnchor = newAnchor,
                        movementSpeed = movementSpeed,
                        rotationSpeed = rotationSpeed,
                        smoothMovement = smoothMovement,
                        onMoveComplete = {
                            isAvatarWalking = false

                            // Play react animation when reached the object
                            (avatarNode.childNodes.firstOrNull() as? ModelNode)?.let { modelNode ->
                                modelNode.stopAnimation(modelNode.playingAnimations.keys.first())
                                modelNode.playAnimation("react")

                                val reactAnimIndex = modelNode.animator.getAnimationIndex("react")
                                val reactAnimDuration = modelNode.animator.getAnimationDuration(reactAnimIndex?: 0)

                                // Return to idle after reacting
                                lifecycleScope.launch {
                                    delay((reactAnimDuration * 1000L).toLong()) // Convert to milliseconds
                                    modelNode.stopAnimation("react")
                                    modelNode.playAnimation("idle")
                                }
                            }
                        }
                    )
                }
            }
        }
    }

    /**
     * Respawns the avatar at the center of the screen by performing a hit test.
     *
     * @param engine The Filament engine used for rendering.
     * @param modelLoader The model loader to load the avatar model.
     * @param frame The current AR frame, used for hit testing.
     * @param childNodes The list of child nodes to which the avatar node will be added.
     */
    fun respawnAvatar(
        engine: Engine,
        modelLoader: ModelLoader,
        frame: Frame?,
        childNodes: MutableList<Node>
    ) {
        val displayMetrics = resources.displayMetrics
        val centerX = displayMetrics.widthPixels / 2f
        val centerY = displayMetrics.heightPixels / 2f
        val hitResults = frame?.hitTest(centerX, centerY)
        hitResults?.firstOrNull {
            it.isValid(
                depthPoint = false,
                point = false
            )
        }?.createAnchorOrNull()
            ?.let { anchor ->
                placeAvatar(
                    engine = engine,
                    modelLoader = modelLoader,
                    anchor = anchor,
                    childNodes = childNodes
                )
            }
    }

    /**
     * Places the avatar at the center of the screen using the provided engine and model loader.
     *
     * @param engine The Filament engine used for rendering.
     * @param modelLoader The model loader to load the avatar model.
     * @param anchor The anchor where the avatar will be placed.
     * @param childNodes The list of child nodes to which the avatar node will be added.
     */
    private fun placeAvatar(
        engine: Engine,
        modelLoader: ModelLoader,
        anchor: Anchor,
        childNodes: MutableList<Node>
    ) {
        // Remove existing avatar if there is one
        currentAnchorNode?.let {
            childNodes.remove(it)
            it.destroy()
        }

        // Create and add the new avatar
        val anchorNode = createAvatarNode(
            engine = engine,
            modelLoader = modelLoader,
            anchor = anchor
        )
        childNodes.add(anchorNode)
        currentAnchorNode = anchorNode
    }

    /**
     * Creates an avatar node at the specified anchor.
     *
     * @param engine The Filament engine used for rendering.
     * @param modelLoader The model loader to load the avatar model.
     * @param anchor The anchor where the avatar will be placed.
     * @return The created AnchorNode containing the avatar model.
     */
    private fun createAvatarNode(
        engine: Engine,
        modelLoader: ModelLoader,
        anchor: Anchor
    ): AnchorNode {
        val anchorNode = AnchorNode(engine = engine, anchor = anchor)
        val modelNode = ModelNode(
            modelInstance = modelLoader.createModelInstance(avatarModelFile),
            autoAnimate = false,
            scaleToUnits = 0.075f
        ).apply {
            // Model Node needs to be editable for independent rotation from the anchor rotation
            isEditable = true
            editableScaleRange = 0.05f..0.05f
            playAnimation("idle")
        }
        anchorNode.addChildNode(modelNode)

        listOf(modelNode, anchorNode).forEach {
            it.onEditingChanged = { editingTransforms ->
                if(editingTransforms.isNotEmpty()) {
                    // Cancel any ongoing movement when editing starts
                    movementJob?.cancel()
                    movementJob = null

                    modelNode.stopAnimation(modelNode.playingAnimations.keys.first())
                    modelNode.playAnimation("pickup")
                }else{
                    modelNode.stopAnimation(modelNode.playingAnimations.keys.first())
                    modelNode.playAnimation("idle")
                }
            }
        }
        return anchorNode
    }
}