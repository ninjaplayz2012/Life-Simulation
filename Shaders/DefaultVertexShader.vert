#version 330 core
layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec2 aPositionScale;
layout (location = 2) in vec4 aColor;

// Object-specific transformations
uniform vec3 Position;       // pixel offset
uniform vec2 PositionScale;  // 0->1, top-left to bottom-right of screen
uniform float Scale;         // dilates around Anchor
uniform mat2 Rotation;       // rotates around Anchor
uniform vec2 Anchor;         // 0->1 pivot within the bounding box
uniform vec2 Size;           // bounding box size in pixels

// Globally managed by your window environment
uniform vec2 WindowSize;
out vec4 vColor;

void main() {
    // 1. Combine per-vertex pixel offset (aPosition) with the anchor offset (aPositionScale * Size)
    vec2 AnchorPixels = Anchor * Size;
    vec2 LocalPixels = (aPositionScale * Size) + aPosition.xy - AnchorPixels;

    // 2. Scale around anchor
    vec2 ScaledSpace = LocalPixels * Scale;

    // 3. Rotate around anchor
    vec2 RotatedSpace = Rotation * ScaledSpace;

    // 4. Move
    vec2 ScreenPosition = PositionScale * WindowSize;
    vec2 FinalPixels = RotatedSpace + ScreenPosition + Position.xy;

    vec2 NDC = (FinalPixels / WindowSize) * 2.0 - 1.0;
    NDC.y = -NDC.y;

    gl_Position = vec4(NDC, Position.z + aPosition.z, 1.0);
    vColor = aColor;
}