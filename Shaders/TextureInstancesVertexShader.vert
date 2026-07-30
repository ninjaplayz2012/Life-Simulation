#version 330 core
layout (location = 0) in vec3 aPosition;
layout (location = 1) in vec2 aPositionScale;
layout (location = 2) in vec2 aTexCoord;
layout (location = 3) in vec4 aColor;

// Per-instance attributes (one value per instance, not per vertex)
layout (location = 4) in vec3 iPosition;
layout (location = 5) in vec2 iPositionScale;
layout (location = 6) in float iScale;
layout (location = 7) in mat2 iRotation;   // consumes locations 6 AND 7 (mat2 = 2 vec2 columns)
layout (location = 9) in vec2 iAnchor;
layout (location = 10) in vec2 iSize;
layout (location = 11) in vec4 iColor;

uniform vec2 WindowSize;
out vec2 vTexCoord;
out vec4 vColor;

void main() {
    vec2 AnchorPixels = iAnchor * iSize;
    vec2 LocalPixels = (aPositionScale * iSize) + aPosition.xy - AnchorPixels;

    vec2 ScaledSpace = LocalPixels * iScale;
    vec2 RotatedSpace = iRotation * ScaledSpace;

    vec2 ScreenPosition = iPositionScale * WindowSize;
    vec2 FinalPixels = RotatedSpace + ScreenPosition + iPosition.xy;

    vec2 NDC = (FinalPixels / WindowSize) * 2.0 - 1.0;
    NDC.y = -NDC.y;

    gl_Position = vec4(NDC, iPosition.z + aPosition.z, 1.0);
    vTexCoord = aTexCoord;
    vColor = iColor * aColor;
}