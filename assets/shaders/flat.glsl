// Vertex Shader
//--------------------------------------------------
#ifdef VERTEX_SHADER
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec2 a_UV;
layout(location = 2) in vec3 a_Normal;
layout(location = 3) in vec4 a_Color;

out vec2 v_UV;
out vec4 v_Color;

uniform mat4 u_ViewProjection;
uniform mat4 u_Transform;

void main()
{
    v_UV = a_UV;
    v_Color = a_Color;
    gl_Position = u_ViewProjection * u_Transform * vec4(a_Position, 1.0);
}
#endif
//--------------------------------------------------

// Fragment Shader
//--------------------------------------------------
#ifdef FRAGMENT_SHADER
in vec2 v_UV;
in vec4 v_Color;

out vec4 color;

uniform float u_TilingFactor;
uniform sampler2D u_Texture;

void main()
{
    // color = texture(u_Texture, v_UV) * v_Color;
    color = vec4(v_UV, 0, 1);
}
#endif
//--------------------------------------------------
