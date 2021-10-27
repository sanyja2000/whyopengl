#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec2 texCoord;
layout(location=2) in vec3 normal;
out vec2 v_TexCoord;
varying vec3 v_position;
varying vec3 v_normal;

uniform mat4 u_MVP;
void main()
{

    gl_Position = u_MVP * vec4(position,1.0);
    v_TexCoord = texCoord;
    v_normal = normalize(normal).xyz;
    v_position = position.xyz;
    
}
