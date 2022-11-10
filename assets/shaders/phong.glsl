// Vertex Shader
//--------------------------------------------------
#ifdef VERTEX_SHADER

layout(location = 0) in vec3 a_Position;
layout(location = 1) in vec2 a_UV;
layout(location = 2) in vec3 a_Normal;

out vec3 v_Normal;
out vec3 v_FragPos;
out vec2 v_UV;

uniform mat4 u_Transform;
uniform mat4 u_ViewProjection;

void main()
{
    gl_Position = u_ViewProjection * u_Transform * vec4(a_Position, 1.0);
    v_FragPos = vec3(u_Transform * vec4(a_Position, 1.0));
    v_Normal = vec3(u_Transform * vec4(a_Normal, 0.0));
    v_UV = a_UV;
}

#endif
//--------------------------------------------------

// Fragment Shader
//--------------------------------------------------
#ifdef FRAGMENT_SHADER

struct Material
{
    // ambient should be same as diffuse
    sampler2D diffuse;
    sampler2D specular;
    vec3 color;
    float shininess;
};

struct DirLight
{
    vec3 direction;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

struct PointLight
{
    vec3 position;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;

    float linear;
    float quadratic;
};

struct SpotLight
{
    vec3 position;
    vec3 direction;
    float cutoff;

    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

const int N_MAX_POINT_LIGHTS = 8;

in vec3 v_FragPos;
in vec3 v_Normal;
in vec2 v_UV;

out vec4 FragColor;

uniform vec3 u_ViewPosition;
uniform Material u_Material;
uniform DirLight u_DirLight;
uniform int u_NPointLights;
uniform PointLight u_PointLights[N_MAX_POINT_LIGHTS];
uniform SpotLight u_SpotLight;

void main()
{
    vec3 ambient = vec3(0.0);
    vec3 diffuse = vec3(0.0);
    vec3 specular = vec3(0.0);
    vec3 lightDir = vec3(0.0);
    vec3 reflectDir = vec3(0.0);
    float strength = 0.0;
    vec3 norm = normalize(v_Normal);
    vec3 viewDir = normalize(u_ViewPosition - v_FragPos);
    vec3 diffuseMap = vec3(texture(u_Material.diffuse, v_UV));
    vec3 specularMap = vec3(texture(u_Material.specular, v_UV));

    // DIRECTIONAL LIGHT
    ambient += diffuseMap * u_DirLight.ambient * u_Material.color;

    lightDir = normalize(-u_DirLight.direction);
    strength = max(dot(norm, lightDir), 0.0);
    diffuse += (strength * diffuseMap) * u_DirLight.diffuse * u_Material.color;

    reflectDir = reflect(-lightDir, norm);
    strength = pow(max(dot(reflectDir, viewDir), 0.0), u_Material.shininess);
    specular += (strength * specularMap) * u_DirLight.specular
                * u_Material.color;

    // POINT LIGHT
    for(int i = 0; i < min(u_NPointLights, N_MAX_POINT_LIGHTS); ++i) {
        float distance = length(u_PointLights[i].position - v_FragPos);
        float attenuation = 1.0 / (1.0 + u_PointLights[i].linear * distance
            + u_PointLights[i].quadratic * (distance * distance));

        ambient += (attenuation * diffuseMap) * u_PointLights[i].ambient
                   * u_Material.color;

        lightDir = normalize(u_PointLights[i].position - v_FragPos);
        strength = max(dot(norm, lightDir), 0.0);
        diffuse += (strength * attenuation * diffuseMap)
                   * u_PointLights[i].diffuse * u_Material.color;

        reflectDir = reflect(-lightDir, norm);
        strength = pow(max(dot(reflectDir, viewDir), 0.0),
                       u_Material.shininess);
        specular += (strength * attenuation * specularMap)
                    * u_PointLights[i].specular * u_Material.color;
    }

    // SPOTLIGHT
    lightDir = normalize(u_SpotLight.position - v_FragPos);
    float val = dot(lightDir, normalize(-u_SpotLight.direction));

    ambient += diffuseMap * u_SpotLight.ambient * u_Material.color;

    if (val > cos(u_SpotLight.cutoff)) {
        strength = max(dot(norm, lightDir), 0.0);
        diffuse += (strength * diffuseMap) * u_SpotLight.diffuse
                   * u_Material.color;

        reflectDir = reflect(-lightDir, norm);
        strength = pow(max(dot(reflectDir, viewDir), 0.0),
                       u_Material.shininess);
        specular += (strength * specularMap) * u_SpotLight.specular
                    * u_Material.color;
    }

    FragColor = vec4(ambient + diffuse + specular, 1.0);
}

#endif
