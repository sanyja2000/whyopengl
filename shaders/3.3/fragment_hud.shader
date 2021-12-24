#version 330
layout(location=0) out vec4 color;

in vec2 v_TexCoord;
uniform sampler2D u_Texture;
uniform int u_time;
void main(){
    vec4 texColor = texture(u_Texture, v_TexCoord);
    if(texColor.a<1.0){
        discard;
    }
    color = texColor;
    //color = vec4(0.8,0.3,0.2,1.0);
}