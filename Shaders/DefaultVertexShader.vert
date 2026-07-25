#version 330 core

layout (location = 0) in vec3 aPos;
layout (location = 1) in vec4 aColor;

out vec4 Color;

uniform float Scale;
uniform mat2 Rotation;
uniform vec3 Position;

void main() {
    gl_Position = vec4(vec3(Rotation * aPos.xy * Scale, aPos.z) + Position, 1.0);
    Color = aColor;
}
