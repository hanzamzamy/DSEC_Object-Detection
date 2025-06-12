package org.hanz.oreoar.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.Alignment
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.sp
import org.hanz.oreoar.ui.panel.ControlPanel

@Composable
/**
 * ScreenOverlay is a composable function that displays an overlay on the screen
 * with information text and a control panel for managing AR objects and avatar actions.
 *
 * @param infoText The text to display at the top of the screen.
 * @param onRespawnClicked Callback invoked when the respawn button is clicked.
 * @param hasSelectedObject Boolean indicating if an object is selected.
 * @param onAddObjectClicked Callback invoked when the add object button is clicked.
 * @param onRemoveObjectClicked Callback invoked when the remove object button is clicked.
 * @param onNavigateToObjectClicked Callback invoked when the navigate to object button is clicked.
 * @param onPlaneRendererChanged Callback invoked when the plane renderer toggle button is clicked.
 */
fun ScreenOverlay(
    infoText: State<String>,
    onRespawnClicked: () -> Unit,
    hasSelectedObject: Boolean = false,
    onAddObjectClicked: () -> Unit = {},
    onRemoveObjectClicked: () -> Unit = {},
    onNavigateToObjectClicked: () -> Unit = {},
    onPlaneRendererChanged: () -> Unit = {},
){
    Box(
        modifier = Modifier
            .fillMaxSize()
            .systemBarsPadding()
    ) {
        // Information text at the top
        Text(
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.TopCenter)
                .padding(top = 16.dp, start = 32.dp, end = 32.dp),
            textAlign = TextAlign.Center,
            fontSize = 28.sp,
            color = Color.White,
            text = infoText.value
        )

        // Control panel at the bottom
        ControlPanel(
            modifier = Modifier
                .align(Alignment.BottomStart)
                .padding(16.dp),
            onRespawnClicked = onRespawnClicked,
            hasSelectedObject = hasSelectedObject,
            onAddObjectClicked = onAddObjectClicked,
            onRemoveObjectClicked = onRemoveObjectClicked,
            onNavigateToObjectClicked = onNavigateToObjectClicked,
            onPlaneRendererChanged = onPlaneRendererChanged,
        )
    }


}