"""
OpenGL Texture Management Module.

Handles OpenGL context and texture creation/updates.
Provides interface for updating overlay textures from PIL images.
"""

from typing import Dict, Optional
from PIL import Image
import glfw
from OpenGL.GL import *

from core.logger import get_logger, ErrorHandler
from core.constants import GL_WINDOW_WIDTH, GL_WINDOW_HEIGHT, GL_WINDOW_VISIBLE

logger = get_logger("GLManager")


class GLManager:
    """
    Manages OpenGL context and textures for VR overlays.

    Features:
    - Creates hidden OpenGL context via GLFW
    - Manages texture creation and updates
    - Handles image-to-texture conversion
    - Prevents flicker through texture management
    - Thread-safe texture operations

    Design:
    - Single context per application
    - Textures stored by name
    - Automatic image resizing and format conversion
    """

    def __init__(self):
        """Initialize OpenGL context and GLFW window."""
        self.window: Optional[any] = None
        self.textures: Dict[str, Dict] = {}
        self._is_initialized = False

        self._init_opengl()

    def _init_opengl(self) -> None:
        """Initialize GLFW and OpenGL context."""
        try:
            if not glfw.init():
                raise RuntimeError("Failed to initialize GLFW")

            # Create hidden window for OpenGL context
            glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
            self.window = glfw.create_window(
                GL_WINDOW_WIDTH,
                GL_WINDOW_HEIGHT,
                "FreeOverlay GL Context",
                None,
                None,
            )

            if not self.window:
                glfw.terminate()
                raise RuntimeError("Failed to create GLFW window")

            glfw.make_context_current(self.window)
            self._is_initialized = True
            logger.info("OpenGL context initialized")

        except Exception as e:
            ErrorHandler.handle(e, context="opengl_init", severity="ERROR")
            self._is_initialized = False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Texture Management
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_texture(
        self,
        name: str,
        width: int,
        height: int,
    ) -> Optional[int]:
        """
        Create a new OpenGL texture.

        Args:
            name: Texture identifier
            width: Texture width in pixels
            height: Texture height in pixels

        Returns:
            OpenGL texture ID or None if creation failed
        """
        if not self._is_initialized:
            logger.error("OpenGL not initialized")
            return None

        try:
            glfw.make_context_current(self.window)

            tex_id = int(glGenTextures(1))
            glBindTexture(GL_TEXTURE_2D, tex_id)

            # Configure texture parameters
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

            # Create empty texture
            glTexImage2D(
                GL_TEXTURE_2D,
                0,
                GL_RGBA8,
                width,
                height,
                0,
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                None,
            )

            glBindTexture(GL_TEXTURE_2D, 0)

            self.textures[name] = {"id": int(tex_id), "w": width, "h": height}
            logger.debug(f"Texture created: {name} ({width}x{height})")
            return int(tex_id)

        except Exception as e:
            ErrorHandler.handle(e, context=f"create_texture_{name}", severity="ERROR")
            return None

    def update_texture(self, name: str, image: Image.Image) -> bool:
        """
        Update a texture with new image data.

        Args:
            name: Texture name
            image: PIL Image

        Returns:
            True if successful
        """
        if not self._is_initialized:
            return False

        if name not in self.textures:
            logger.warning(f"Texture not found: {name}")
            return False

        try:
            glfw.make_context_current(self.window)

            tex = self.textures[name]

            # Convert image to RGBA if needed
            if image.mode != "RGBA":
                image = image.convert("RGBA")

            # Ensure correct size
            if image.size != (tex["w"], tex["h"]):
                image = image.resize(
                    (tex["w"], tex["h"]),
                    Image.Resampling.LANCZOS,
                )

            # Flip vertically for OpenGL
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)

            # Get image data
            data = image.tobytes()

            # Update texture
            glBindTexture(GL_TEXTURE_2D, int(tex["id"]))
            glTexSubImage2D(
                GL_TEXTURE_2D,
                0,
                0,
                0,
                tex["w"],
                tex["h"],
                GL_RGBA,
                GL_UNSIGNED_BYTE,
                data,
            )
            glFlush()
            glBindTexture(GL_TEXTURE_2D, 0)

            return True

        except Exception as e:
            ErrorHandler.handle(
                e,
                context=f"update_texture_{name}",
                severity="WARNING",
            )
            return False

    def get_texture_id(self, name: str) -> int:
        """
        Get OpenGL texture ID by name.

        Args:
            name: Texture name

        Returns:
            OpenGL texture ID or 0 if not found
        """
        if name in self.textures:
            return int(self.textures[name]["id"])
        return 0

    def delete_texture(self, name: str) -> bool:
        """
        Delete a texture by name.

        Args:
            name: Texture name

        Returns:
            True if deleted
        """
        if name not in self.textures:
            return False

        try:
            glfw.make_context_current(self.window)
            tex = self.textures[name]
            glDeleteTextures(1, [int(tex["id"])])
            del self.textures[name]
            logger.debug(f"Texture deleted: {name}")
            return True
        except Exception as e:
            ErrorHandler.handle(e, context=f"delete_texture_{name}")
            return False

    def list_textures(self) -> list:
        """Get list of all texture names."""
        return list(self.textures.keys())

    # ═══════════════════════════════════════════════════════════════════════════════
    # Cleanup
    # ═══════════════════════════════════════════════════════════════════════════════

    def shutdown(self) -> None:
        """Clean up OpenGL resources."""
        try:
            if not self._is_initialized:
                return

            glfw.make_context_current(self.window)

            # Delete all textures
            for name in list(self.textures.keys()):
                self.delete_texture(name)

            if self.window:
                glfw.destroy_window(self.window)

            glfw.terminate()
            self._is_initialized = False
            logger.info("OpenGL shutdown complete")

        except Exception as e:
            ErrorHandler.handle(e, context="opengl_shutdown", severity="WARNING")

    def __del__(self):
        """Ensure cleanup on garbage collection."""
        self.shutdown()

    def is_initialized(self) -> bool:
        """Check if OpenGL context is ready."""
        return self._is_initialized
