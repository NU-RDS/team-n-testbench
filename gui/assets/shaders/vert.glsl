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
    mat4 mvp = u_proj * u_view * u_model;
    vec4 pos = mvp * vec4(a_position, 1.0);

    // check that the vertex is in front of the camera
    if(pos.z < 0.0) {
        // if not, set the vertex position to the origin
        pos = vec4(0.0, 0.0, 0.0, 0.0);
    }

    pos = pos / pos.w;
    gl_Position = pos;

    // Pass the normal to the fragment shader
    vec4 normal = u_model * vec4(a_normal, 0.0);
    v_normal = normal.xyz;
    v_fragPos = vec3(u_model * vec4(a_position, 1.0));
}
