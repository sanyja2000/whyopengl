#version 330
layout(location=0) out vec4 color;

in vec2 v_TexCoord;
uniform sampler2D u_Texture;
uniform int u_time;
void main(){
    //vec2 sampleCoord = vec2(v_TexCoord.x, mod(v_TexCoord.y+u_time/1000.0,1.0));
    // vec4 texColor = texture(u_Texture, sampleCoord);
    vec3 blue = vec3(0,0.25,0.62);
    vec4 texColor = vec4(mix(blue,vec3(0,0,0),v_TexCoord.x),1.0);
    if(v_TexCoord.x<0.25){
        if(v_TexCoord.x<(sin(v_TexCoord.y*10+u_time/100.0)+1)/40+cos(v_TexCoord.y*25-u_time/130.0)/90+0.1){
            discard;
        }
        if(mod(pow(v_TexCoord.x,2.0),0.01)<0.005 || mod(v_TexCoord.y,0.015)<0.008){
            //discard;
        }
    }
    if(texColor.a<1.0){
        discard;
    }
    color = texColor;
    
    
    //color = vec4(0.8,0.3,0.2,1.0);
}