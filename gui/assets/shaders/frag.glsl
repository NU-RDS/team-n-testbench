#version 330 core

// Inputs from the vertex shader.
in vec3 v_normal;
in vec3 v_fragPos;

// Uniform color
uniform vec3 u_color;

// Output fragment color.
out vec4 FragColor;

void main()
{
    // Normalize the interpolated normal.
    vec3 norm = normalize(v_normal);
    
    // Define a fixed light direction (pointing along the positive Z axis).
    vec3 lightDir = normalize(vec3(0.0, 0.0, 1.0));
    
    // Compute a simple diffuse lighting factor.
    float diff = max(dot(norm, lightDir), 0.0);
    
    // Multiply the uniform color by the diffuse factor.
    vec3 diffuse = diff * u_color;
    
    // Set the fragment's output color.
    FragColor = vec4(diffuse, 1.0);
}