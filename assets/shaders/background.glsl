// Vertex Shader
//--------------------------------------------------
#ifdef VERTEX_SHADER
layout (location = 0) in vec3 a_Position;

out vec3 v_TexCoord;

uniform mat4 u_ViewProjection;

void main()
{
    v_TexCoord = a_Position;
    vec4 pos = u_ViewProjection * vec4(a_Position, 1.0);

    // optimzation purpose - render skybox last
    // make depth equal 1.0 after "perspective division"
    gl_Position = pos.xyww;
}
#endif
//--------------------------------------------------

// Fragment Shader
//--------------------------------------------------
#ifdef FRAGMENT_SHADER

in vec3 v_TexCoord;

out vec4 FragColor;

uniform samplerCube u_Cubemap;
uniform bool u_UsingHDR;

void main()
{
    vec3 envColor = texture(u_Cubemap, v_TexCoord).rgb;

    if (u_UsingHDR) {
        envColor = envColor / (envColor + vec3(1.0));
        envColor = pow(envColor, vec3(1.0/2.2));
    }

    FragColor = vec4(envColor, 1.0);
}
#endif
//--------------------------------------------------
