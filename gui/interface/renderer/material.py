import glm

class MaterialProperties:
    def __init__(self):
        self.shader = 0
        self.color = glm.vec3(0.0, 0.0, 0.0)  # Using glm.vec3 for color


class Material:
    def __init__(self, shader: int, properties: MaterialProperties):
        self.shader = shader
        self.properties = properties