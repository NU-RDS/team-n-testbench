#version 330 core

// Inputs from the vertex shader.
in vec3 v_normal;
in vec3 v_fragPos;

// Uniform color
uniform vec3 u_color;
uniform bool u_fade;
uniform vec3 u_cameraPos;

// Output fragment color.
out vec4 FragColor;

void main()
{
    // Normalize the normal because it's interpolated and not 1.0 in length.
    vec3 normal = normalize(v_normal);
    
    // Ambient lighting
    float ambientStrength = 0.1;
    vec3 ambient = ambientStrength * u_color;
    
    // Diffuse lighting
    vec3 lightDir = normalize(vec3(0.0, 1.0, 1.0));
    float diff = max(dot(normal, lightDir), 0.0);
    vec3 diffuse = diff * u_color;
    
    // Specular lighting
    float specularStrength = 0.5;
    vec3 viewDir = normalize(vec3(0.0, 0.0, 1.0));
    vec3 reflectDir = reflect(-lightDir, normal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = specularStrength * spec * u_color;
    
    // Combine all the lighting components
    vec3 result = (ambient + diffuse + specular) * u_color;

    // fade the color based on the distance from the camera
    float distance = length(u_cameraPos - v_fragPos);
    float fade = 1.0 - smoothstep(0.0, 30.0, distance);

    if (!u_fade) {
        fade = 1.0;
    }

    
    // Output the fragment color
    FragColor = vec4(result, fade);
}