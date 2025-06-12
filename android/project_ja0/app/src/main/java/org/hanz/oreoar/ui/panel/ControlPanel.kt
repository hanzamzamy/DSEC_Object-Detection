package org.hanz.oreoar.ui.panel

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Place


@Composable
/** ControlPanel is a composable function that displays a row of control buttons
 * for managing AR objects and avatar actions.
 *
 * @param modifier Modifier to apply to the ControlPanel.
 * @param onRespawnClicked Callback invoked when the respawn button is clicked.
 * @param hasSelectedObject Boolean indicating if an object is selected.
 * @param onAddObjectClicked Callback invoked when the add object button is clicked.
 * @param onRemoveObjectClicked Callback invoked when the remove object button is clicked.
 * @param onNavigateToObjectClicked Callback invoked when the navigate to object button is clicked.
 * @param onPlaneRendererChanged Callback invoked when the plane renderer toggle button is clicked.
 */
fun ControlPanel(
    modifier: Modifier = Modifier,
    onRespawnClicked: () -> Unit,
    hasSelectedObject: Boolean = false,
    onAddObjectClicked: () -> Unit = {},
    onRemoveObjectClicked: () -> Unit = {},
    onNavigateToObjectClicked: () -> Unit = {},
    onPlaneRendererChanged: () -> Unit = {},
) {
    // Control buttons row
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        // Plane renderer toggle button
        Button(
            onClick = onPlaneRendererChanged,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xDDFF5722)
            ),
            contentPadding = PaddingValues(8.dp),
            modifier = Modifier.size(56.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Clear,
                contentDescription = "Toggle Plane Renderer",
                tint = Color.White
            )
        }

        // Respawn button
        Button(
            onClick = onRespawnClicked,
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xDDFF5722)
            ),
            contentPadding = PaddingValues(8.dp),
            modifier = Modifier.size(56.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Refresh,
                contentDescription = "Respawn Avatar",
                tint = Color.White
            )
        }

        // Add object button
        Button(
            onClick = onAddObjectClicked,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xDD2196F3)),
            contentPadding = PaddingValues(8.dp),
            modifier = Modifier.size(56.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Add,
                contentDescription = "Add Object",
                tint = Color.White
            )
        }

        // Button that appears only if an object is selected
        if (hasSelectedObject) {
            // Remove object button
            Button(
                onClick = onRemoveObjectClicked,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xDDF44336)),
                contentPadding = PaddingValues(8.dp),
                modifier = Modifier.size(56.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Delete,
                    contentDescription = "Remove Object",
                    tint = Color.White
                )
            }

            // Navigate to Object button
            Button(
                onClick = onNavigateToObjectClicked,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xDD4CAF50)),
                contentPadding = PaddingValues(8.dp),
                modifier = Modifier.size(56.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Place,
                    contentDescription = "Navigate Avatar",
                    tint = Color.White
                )
            }
        }
    }
}
