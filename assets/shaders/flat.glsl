#ifdef VERTEX_SHADER
layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec2 a_UV;

out vec2 v_UV;

uniform mat4 u_ViewProjection;
uniform mat4 u_Transform;

void main()
{
    v_UV = a_UV;
    gl_Position = u_ViewProjection * u_Transform * vec4(a_Position, 1.0);
}
#endif

#ifdef FRAGMENT_SHADER

in vec2 v_UV;
in vec4 v_Color;

out vec4 color;

uniform float u_TilingFactor;
uniform sampler2D u_Texture;
uniform vec4 u_Color;

void main()
{
    color = texture(u_Texture, v_UV) * u_Color;
}
#endif
