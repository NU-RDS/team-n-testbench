import enum
import glm
from interface.renderer.scene_graph import Transform

class CameraMode(enum.Enum):
    """Camera mode enumeration."""
    ORTHOGRAPHIC = 0
    PERSPECTIVE = 1

class PerspectiveCamera:
    def __init__(self, fov: float, aspect_ratio: float, near: float, far: float):
        self.fov = fov
        self.aspect_ratio = aspect_ratio
        self.near = near
        self.far = far

    def get_projection_matrix(self):
        return glm.perspective(self.fov, self.aspect_ratio, self.near, self.far)

class OrthographicCamera:
    def __init__(self, left: float, right: float, bottom: float, top: float, near: float, far: float):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top
        self.near = near
        self.far = far

    def get_projection_matrix(self):
        return glm.ortho(self.left, self.right, self.bottom, self.top, self.near, self.far)

class Camera:
    def __init__(self, mode: CameraMode, transform: Transform):
        self.mode = mode
        self.transform = transform
        self.perspective = None
        self.orthographic = None

    @staticmethod
    def perspective(fov: float, aspect_ratio: float, near: float, far: float) -> "Camera":
        camera = Camera(CameraMode.PERSPECTIVE, Transform())
        camera.perspective = PerspectiveCamera(fov, aspect_ratio, near, far)
        return camera
    
    @staticmethod
    def orthographic(left: float, right: float, bottom: float, top: float, near: float, far: float) -> "Camera":
        camera = Camera(CameraMode.ORTHOGRAPHIC, Transform())
        camera.orthographic = OrthographicCamera(left, right, bottom, top, near, far)
        return camera
    
    @staticmethod
    def default() -> "Camera":
        camera = Camera.perspective(45.0, 1.0, 0.1, 1000.0)
        camera.transform.position = glm.vec3(-10.0, 10.0, -10.0)
        # set the camera to look at the origin
        camera.transform.rotation = glm.angleAxis(glm.radians(-135.0), glm.vec3(1.0, 0.0, 0.0))

        return camera
    
    def update_aspect_ratio(self, aspect_ratio: float):
        if self.mode == CameraMode.PERSPECTIVE:
            self.perspective.aspect_ratio = aspect_ratio
        elif self.mode == CameraMode.ORTHOGRAPHIC:
            self.orthographic.right = aspect_ratio
            self.orthographic.left = -aspect_ratio


    def set_perspective(self, fov: float, aspect_ratio: float, near: float, far: float):
        self.mode = CameraMode.PERSPECTIVE
        self.perspective = PerspectiveCamera(fov, aspect_ratio, near, far)

    def set_orthographic(self, left: float, right: float, bottom: float, top: float, near: float, far: float):
        self.mode = CameraMode.ORTHOGRAPHIC
        self.orthographic = OrthographicCamera(left, right, bottom, top, near, far)

    def get_projection_matrix(self):
        if self.mode == CameraMode.PERSPECTIVE:
            return self.perspective.get_projection_matrix()
        elif self.mode == CameraMode.ORTHOGRAPHIC:
            return self.orthographic.get_projection_matrix()
        
    def get_view_matrix(self):
        return glm.inverse(self.transform.get_matrix())