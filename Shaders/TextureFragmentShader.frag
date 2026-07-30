#version 330 core
in vec2 vTexCoord;
in vec4 vColor;

uniform sampler2D CurrentTexture;
out vec4 FragColor;

void main() {
    FragColor = texture(CurrentTexture, vTexCoord) * vColor;
}