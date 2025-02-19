#version 330 core

// Input attributes
layout(location = 0) in vec3 a_position;
layout(location = 1) in vec3 a_normal;

// Uniform transformation matrices
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_proj;

// Outputs to the fragment shader
out vec3 v_normal;
out vec3 v_fragPos;

void main()
{
    // Transform the vertex position into world space.
    vec4 worldPosition = u_model * vec4(a_position, 1.0);
    v_fragPos = worldPosition.xyz;
    
    // Transform the normal.
    // Using the inverse transpose of the model matrix ensures correct normal transformation.
    v_normal = mat3(transpose(inverse(u_model))) * a_normal;
    
    // Transform the position into clip space.
    gl_Position = u_proj * u_view * worldPosition;
}
