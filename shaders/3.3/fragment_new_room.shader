#version 330 core
layout(location=0) out vec4 color;

in vec2 v_TexCoord;
varying vec3 v_position;
varying vec3 v_normal;

uniform sampler2D u_Texture;

void main(){

    vec4 texColor = texture(u_Texture, v_TexCoord)*(0.7-v_position.y/2.0);
    if(v_normal.y<0){
      texColor = texture(u_Texture, v_TexCoord)*0.5;
      texColor.z += 0.1;
    }

    color = vec4(texColor.xyz,1.0);
    //color = vec4(0.8,0.3,0.2,1.0);
}
