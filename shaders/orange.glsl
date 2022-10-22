// Vertex Shader
//--------------------------------------------------
#ifdef VERTEX_SHADER

layout(location = 0) in vec3 a_Position;

uniform mat4 u_Transform;
uniform mat4 u_ViewProjection;

void main()
{
    gl_Position = u_ViewProjection * u_Transform * vec4(a_Position, 1.0);
}

#endif
//--------------------------------------------------

// Fragment Shader
//--------------------------------------------------
#ifdef FRAGMENT_SHADER

precision mediump float;

out vec4 FragColor;

void main()
{
    FragColor = vec4(1.0, 0.7, 0.0, 1.0);
}

#endif
//--------------------------------------------------
