package org.hanz.oreoar.ml.detector

/**
 * Represents a detected object with its label, confidence score, bounding box, center point, and size.
 *
 * @property label The label of the detected object.
 * @property confidence The confidence score of the detection (0.0 to 1.0).
 * @property boundingBox The bounding box of the detected object.
 * @property center The center point of the detected object.
 * @property size The size of the detected object.
 */
data class Detection(
    val label: String,
    val confidence: Float,
    val boundingBox: BoundingBox,
    val center: Point,
    val size: Size
) {
    /**
     * Represents a bounding box defined by its top-left and bottom-right coordinates.
     * @property x1 The x-coordinate of the top-left corner.
     * @property y1 The y-coordinate of the top-left corner.
     * @property x2 The x-coordinate of the bottom-right corner.
     * @property y2 The y-coordinate of the bottom-right corner.
     */
    data class BoundingBox(
        val x1: Float,
        val y1: Float,
        val x2: Float,
        val y2: Float
    )

    /**
     * Represents a point in 2D space.
     * @property x The x-coordinate of the point.
     * @property y The y-coordinate of the point.
     */
    data class Point(val x: Float, val y: Float)

    /**
     * Represents the size of the detected object.
     * @property width The width of the object.
     * @property height The height of the object.
     */
    data class Size(val width: Float, val height: Float)
}
