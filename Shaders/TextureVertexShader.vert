#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTex;

out vec2 TextureCoordinate;

uniform float Scale;
uniform mat2 Rotation;
uniform vec3 Position;

void main() {
    gl_Position = vec4(vec3(Rotation * aPos * Scale, 0.0) + Position, 1.0);
    TextureCoordinate = aTex;
}
