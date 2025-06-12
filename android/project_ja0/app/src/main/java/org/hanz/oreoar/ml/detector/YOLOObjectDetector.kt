package org.hanz.oreoar.ml.detector

import android.content.Context
import android.graphics.*
import android.media.Image
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.Interpreter.Options
import org.tensorflow.lite.support.common.FileUtil
import org.tensorflow.lite.support.common.ops.NormalizeOp
import org.tensorflow.lite.support.image.ImageProcessor
import org.tensorflow.lite.support.image.ImageProcessor.Builder
import org.tensorflow.lite.support.image.TensorImage
import java.io.ByteArrayOutputStream
import android.util.Log
import kotlin.math.max
import kotlin.math.min

/**
 * YOLO Object Detector using TensorFlow Lite.
 * This class initializes the TFLite interpreter and provides methods to process images
 * and detect objects using a YOLO model.
 *
 * @param context The application context.
 * @param modelFilePath The file path of the TFLite model.
 * @param confidenceThreshold The confidence threshold for filtering detections.
 * @param iouThreshold The IoU threshold for Non-Maximum Suppression (NMS).
 */
class YOLOObjectDetector(
    private val context: Context,
    modelFilePath: String = "detection_model.tflite",
    private val confidenceThreshold: Float = 0.85f,
    private val iouThreshold: Float = 0.8f,
    private val maxDetection: Int = 300
) {
    private val interpreter: Interpreter

    init {
        try {
            val modelBuffer = FileUtil.loadMappedFile(context, modelFilePath)
            val interpretOptions = Options()
            interpretOptions.setNumThreads(2) // Set number of threads for inference
            interpreter = Interpreter(modelBuffer, interpretOptions)
            Log.d(TAG, "TFLite interpreter initialized successfully")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load TFLite model", e)
            throw RuntimeException("Failed to load TFLite model", e)
        }
    }

    /**
     * Processes an image and returns a list of detected objects.
     * @param image The input image to process.
     * @return A list of Detection objects containing detected objects' information.
     */
    fun processImage(image: Image): List<Detection> {
        try {
            val bitmap = imageToBitmap(image)

            if (bitmap == null) {
                Log.e(TAG, "Failed to convert image to bitmap")
                throw RuntimeException("Failed to convert image to bitmap")
            }

            val originalWidth = bitmap.width
            val originalHeight = bitmap.height

            var tensorImage = TensorImage()
            tensorImage.load(bitmap)

            val imageProcessor: ImageProcessor = Builder()
                .add(NormalizeOp(0f, 255f)) // Normalize to [0,1]
                .build()
            tensorImage = imageProcessor.process(tensorImage)

            Log.d(TAG, "Image processed: ${tensorImage.width}x${tensorImage.height}, shape=${tensorImage.tensorBuffer.shape.contentToString()}")

            val output: Array<Array<FloatArray>> =
                Array(OUTPUT_BATCH) {
                    Array(OUTPUT_PREDICTIONS) {
                        FloatArray(VALUES_PER_DETECTION)
                    }
                }
            interpreter.run(tensorImage.buffer, output)

            val detections = interpret(
                output = output[0],
                confThreshold = confidenceThreshold,
                iouThreshold = iouThreshold,
                inputShape = Pair(originalWidth,originalHeight ),
                label = LABELS[0] // Don't care, single class model for now
            )

            return detections
        } catch (e: Exception) {
            Log.e(TAG, "Error processing image: " + e.message, e)
            throw RuntimeException("Error processing image: " + e.message, e)
        }
    }

    /**
     * Converts an Image object to a Bitmap.
     * @param image The Image object to convert.
     * @return A Bitmap representation of the image, or null if conversion fails.
     */
    private fun imageToBitmap(image: Image): Bitmap? {
        val planes = image.planes
        val yBuffer = planes[0]!!.buffer
        val uBuffer = planes[1]!!.buffer
        val vBuffer = planes[2]!!.buffer

        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()

        val nv21 = ByteArray(ySize + uSize + vSize)

        yBuffer.get(nv21, 0, ySize)
        vBuffer.get(nv21, ySize, vSize)
        uBuffer.get(nv21, ySize + vSize, uSize)

        val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height, null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(Rect(0, 0, yuvImage.width, yuvImage.height), 100, out)

        val imageBytes = out.toByteArray()
        val bitmap = BitmapFactory.decodeByteArray(imageBytes, 0, imageBytes.size)

        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height)
    }

    /**
     * Converts a bounding box from [center_x, center_y, width, height] format to [x1, y1, x2, y2] pixel format.
     * @param box The bounding box in [center_x, center_y, width, height] format (normalized).
     * @param inputW The width of the input image in pixels.
     * @param inputH The height of the input image in pixels.
     * @return A FloatArray containing [x1, y1, x2, y2] coordinates in pixel space.
     */
    fun xywh2xyxyPixel(box: FloatArray, inputW: Int, inputH: Int): FloatArray {
        val cx = box[0] * inputW
        val cy = box[1] * inputH
        val w = box[2] * inputW
        val h = box[3] * inputH
        val x1 = cx - w / 2f
        val y1 = cy - h / 2f
        val x2 = cx + w / 2f
        val y2 = cy + h / 2f
        return floatArrayOf(x1, y1, x2, y2)
    }

    /**
     * Calculates the Intersection over Union (IoU) between two bounding boxes.
     * @param boxA The first bounding box in [x1, y1, x2, y2] format.
     * @param boxB The second bounding box in [x1, y1, x2, y2] format.
     * @return The IoU value between the two boxes (0.0 to 1.0).
     */
    fun iou(boxA: FloatArray, boxB: FloatArray): Float {
        val xA = max(boxA[0], boxB[0])
        val yA = max(boxA[1], boxB[1])
        val xB = min(boxA[2], boxB[2])
        val yB = min(boxA[3], boxB[3])
        val interW = max(0f, xB - xA)
        val interH = max(0f, yB - yA)
        val interArea = interW * interH
        val boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        val boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        return if (interArea > 0f) interArea / (boxAArea + boxBArea - interArea) else 0f
    }

    /**
     * Non-Maximum Suppression (NMS) to filter overlapping bounding boxes.
     * @param boxes List of bounding boxes in [x1, y1, x2, y2] format.
     * @param scores List of confidence scores for each box.
     * @param iouThreshold IoU threshold for filtering boxes.
     * @param maxDet Maximum number of detections to keep.
     * @return List of indices of the kept boxes.
     */
    fun nms(
        boxes: List<FloatArray>,
        scores: List<Float>,
        iouThreshold: Float,
        maxDet: Int = maxDetection
    ): List<Int> {
        val indices = scores.indices.sortedByDescending { scores[it] }.toMutableList()
        val keep = mutableListOf<Int>()
        while (indices.isNotEmpty() && keep.size < maxDet) {
            val current = indices.removeAt(0)
            keep.add(current)
            indices.removeAll { i -> iou(boxes[current], boxes[i]) > iouThreshold }
        }
        return keep
    }

    /**
     * Interprets the model output and extracts detections.
     * @param output The model output containing bounding boxes and confidence scores.
     * @param confThreshold Confidence threshold for filtering detections.
     * @param iouThreshold IoU threshold for Non-Maximum Suppression (NMS).
     * @param inputShape The shape of the input image (width, height).
     * @param label The label for the detected objects.
     * @return A list of Detection objects containing detected objects' information.
     */
    fun interpret(
        output: Array<FloatArray>,
        confThreshold: Float,
        iouThreshold: Float,
        inputShape: Pair<Int, Int>,
        label: String
    ): List<Detection> {
        val inputW = inputShape.first
        val inputH = inputShape.second
        val numBoxes = output[0].size
        val boxes = mutableListOf<FloatArray>()
        val scores = mutableListOf<Float>()

        // 1. Gather candidates above confidence threshold
        for (i in 0 until numBoxes) {
            val conf = output[4][i]
            if (conf > confThreshold) {
                // Box is in [center_x, center_y, w, h] format, normalized
                val box = FloatArray(4) { output[it][i] }
                boxes.add(xywh2xyxyPixel(box, inputW, inputH))
                scores.add(conf)
            }
        }

        // 2. Apply NMS
        val keep = nms(boxes, scores, iouThreshold)

        // 3. Output in pixel space
        val detections = mutableListOf<Detection>()
        for (idx in keep) {
            val box = boxes[idx]
            val x1 = box[0]
            val y1 = box[1]
            val x2 = box[2]
            val y2 = box[3]
            val cx = (x1 + x2) / 2f
            val cy = (y1 + y2) / 2f
            val width = x2 - x1
            val height = y2 - y1

            detections.add(
                Detection(
                    label = label,
                    confidence = scores[idx],
                    boundingBox = Detection.BoundingBox(x1, y1, x2, y2),
                    center = Detection.Point(cx, cy),
                    size = Detection.Size(width, height)
                )
            )
        }
        return detections
    }

    companion object {
        private const val TAG = "ObjectDetector"

        // Model output tensor shape is [1, 5, 6300]
        private const val OUTPUT_BATCH = 1              // Single batch inference
        private const val OUTPUT_PREDICTIONS = 5        // 4 bounding box parameters + 1 confidence score
        private const val VALUES_PER_DETECTION = 6300   // 6300 detections per image
        private val LABELS = listOf("Oreo")
    }
}