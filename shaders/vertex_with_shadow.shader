#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec2 aTexCoords;
layout (location = 2) in vec3 aNormal;


out VS_OUT {
    vec3 FragPos;
    vec3 Normal;
    vec2 TexCoords;
    vec4 FragPosLightSpace;
} vs_out;

uniform mat4 u_VP;
uniform mat4 u_model;
uniform mat4 u_shadowMatrix;

void main()
{    
    vs_out.FragPos = vec3(transpose(u_model) * vec4(aPos, 1.0));
    vs_out.Normal = transpose(inverse(mat3(transpose(u_model)))) * aNormal;
    vs_out.TexCoords = aTexCoords;
    vs_out.FragPosLightSpace = transpose(u_shadowMatrix) * vec4(vs_out.FragPos, 1.0);
    gl_Position = transpose(u_VP) * vec4(vs_out.FragPos, 1.0);
}