package org.hanz.oreoar

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.*
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.lifecycleScope
import com.google.ar.core.Config
import com.google.ar.core.Frame
import com.google.ar.core.TrackingFailureReason
import io.github.sceneview.*
import io.github.sceneview.ar.ARScene
import io.github.sceneview.ar.arcore.createAnchorOrNull
import io.github.sceneview.ar.arcore.isValid
import io.github.sceneview.ar.getDescription
import io.github.sceneview.ar.rememberARCameraNode
import org.hanz.oreoar.ui.theme.OreoARTheme

import org.hanz.oreoar.ar.entity.AvatarController
import org.hanz.oreoar.ar.entity.ObjectManager
import org.hanz.oreoar.ar.scene.SceneManager
import org.hanz.oreoar.ml.detector.YOLOObjectDetector
import org.hanz.oreoar.ui.ScreenOverlay

private const val avatarModelFile = "ar/junko.glb"
private const val detectorModelFile = "ml/cookie_v1.tflite"

class MainActivity : ComponentActivity() {
    private var objectDetector : YOLOObjectDetector? = null
    private var avatarControlller: AvatarController? = null
    private var objectManager: ObjectManager? = null
    private var sceneManager: SceneManager? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        objectDetector = YOLOObjectDetector(
            context = this,
            modelFilePath = detectorModelFile,
            confidenceThreshold = 0.85f,
            iouThreshold = 0.8f
        )

        avatarControlller = AvatarController(
            resources = resources,
            lifecycleScope = lifecycleScope,
            avatarModelFile = avatarModelFile,
        )

        objectManager = ObjectManager()

        sceneManager = SceneManager(
            objectDetector = objectDetector,
            objectManager = objectManager
        )

        setContent {
            OreoARTheme {
                // A surface container using the 'background' color from the theme
                Box(
                    modifier = Modifier.fillMaxSize(),
                ) {
                    // The destroy calls are automatically made when their disposable effect leaves
                    // the composition or its key changes.
                    val engine = rememberEngine()
                    val modelLoader = rememberModelLoader(engine)
                    val materialLoader = rememberMaterialLoader(engine)
                    val cameraNode = rememberARCameraNode(engine)
                    val childNodes = rememberNodes()
                    val view = rememberView(engine)
                    val collisionSystem = rememberCollisionSystem(view)

                    var planeRenderer by remember { mutableStateOf(true) }

                    var trackingFailureReason by remember {
                        mutableStateOf<TrackingFailureReason?>(null)
                    }
                    var frame by remember { mutableStateOf<Frame?>(null) }

                    ARScene(
                        modifier = Modifier.fillMaxSize(),
                        childNodes = childNodes,
                        engine = engine,
                        view = view,
                        modelLoader = modelLoader,
                        collisionSystem = collisionSystem,
                        sessionConfiguration = { session, config ->
                            config.depthMode =
                                when (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
                                    true -> Config.DepthMode.AUTOMATIC
                                    else -> Config.DepthMode.DISABLED
                                }
                            config.instantPlacementMode = Config.InstantPlacementMode.LOCAL_Y_UP
                            config.lightEstimationMode = Config.LightEstimationMode.ENVIRONMENTAL_HDR
                        },
                        cameraNode = cameraNode,
                        planeRenderer = planeRenderer,
                        onTrackingFailureChanged = {
                            trackingFailureReason = it
                        },
                        onSessionUpdated = { session, updatedFrame ->
                            frame = updatedFrame
                        },
                        onGestureListener = rememberOnGestureListener(
                            onDoubleTapEvent = { motionEvent, node ->
                                if (node == null && avatarControlller?.currentAnchorNode != null && !avatarControlller?.isAvatarWalking!!) {
                                    val hitResults = frame?.hitTest(motionEvent.x, motionEvent.y)
                                    hitResults?.firstOrNull {
                                        it.isValid(depthPoint = false, point = false)
                                    }?.createAnchorOrNull()?.let { newAnchor ->
                                        avatarControlller?.moveAvatarToLocation(newAnchor = newAnchor)
                                    }
                                }
                            },

                            onSingleTapConfirmed = { motionEvent, node ->
                                if (node != null) {
                                    // Check if tapped on an object
                                    val hitAnchorNode = objectManager?.objectNodes?.find { it.childNodes.contains(node) }
                                    if (hitAnchorNode != null) {
                                        objectManager?.selectObject(hitAnchorNode)
                                        return@rememberOnGestureListener
                                    }
                                }
                            })
                    )

                    ScreenOverlay(
                        infoText = trackingFailureReason?.getDescription(LocalContext.current) ?: if (avatarControlller?.currentAnchorNode == null) {
                            stringResource(R.string.point_your_phone_down)
                        } else {
                            stringResource(R.string.tap_anywhere_to_add_model)
                        },
                        onRespawnClicked = {
                            avatarControlller?.respawnAvatar(
                                engine = engine,
                                modelLoader = modelLoader,
                                frame = frame,
                                childNodes = childNodes
                            )
                        },
                        hasSelectedObject = objectManager?.selectedObjectNode != null,
                        onAddObjectClicked = {
                            frame?.let {
                                sceneManager?.processFrameForDetection(
                                    frame = it,
                                    childNodes = childNodes,
                                    engine = engine,
                                    materialLoader = materialLoader
                                )
                            }
                        },
                        onRemoveObjectClicked = {
                            objectManager?.removeSelectedObject(childNodes)
                        },
                        onNavigateToObjectClicked = {
                            objectManager?.selectedObjectNode?.let { selectedNode ->
                                avatarControlller?.navigateAvatarToObject(selectedNode, objectManager!!.marginSize)
                            }
                        },
                        onPlaneRendererChanged = { planeRenderer = !planeRenderer }
                    )
                }
            }
        }
    }
}
