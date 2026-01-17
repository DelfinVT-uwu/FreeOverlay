"""
VR Manager Module.

Abstracts OpenVR functionality for overlay creation and pose tracking.
Provides high-level interface for VR operations.
"""

from typing import Optional, Tuple
import numpy as np
import openvr
import ctypes

from core.logger import get_logger, ErrorHandler
from utils.math_utils import mat34_to_numpy

logger = get_logger("VRManager")


class VRManager:
    """
    High-level abstraction for OpenVR functionality.

    Handles:
    - VR system initialization
    - Overlay creation and management
    - Pose tracking
    - Texture assignment
    - Clean shutdown

    Design:
    - Single instance per application
    - Error-safe operations with logging
    - Resource cleanup on exit
    """

    def __init__(self):
        """Initialize VR system and get overlay interface."""
        self.vr_system: Optional[any] = None
        self.overlay_interface: Optional[any] = None
        self.is_initialized = False

        self._init_vr()

    def _init_vr(self) -> None:
        """Initialize OpenVR system."""
        try:
            openvr.init(openvr.VRApplication_Overlay)
            self.vr_system = openvr.VRSystem()
            self.overlay_interface = openvr.IVROverlay()
            self.is_initialized = True
            logger.info("OpenVR initialized successfully")
        except Exception as e:
            ErrorHandler.handle(e, context="vr_init", severity="ERROR")
            self.is_initialized = False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Overlay Management
    # ═══════════════════════════════════════════════════════════════════════════════

    def create_overlay(
        self,
        overlay_name: str,
        overlay_title: str,
        sort_order: int = 1,
    ) -> Optional[int]:
        """
        Create a new overlay.

        Args:
            overlay_name: Internal name (must be unique)
            overlay_title: Display title
            sort_order: Render order (higher = on top)

        Returns:
            Overlay handle or None if creation failed
        """
        if not self.is_initialized:
            logger.error("VR system not initialized")
            return None

        try:
            handle = self.overlay_interface.createOverlay(overlay_name, overlay_title)
            self.overlay_interface.setOverlaySortOrder(handle, sort_order)
            logger.info(f"Overlay created: {overlay_name} (handle={handle})")
            return handle
        except Exception as e:
            ErrorHandler.handle(
                e,
                context=f"create_overlay_{overlay_name}",
                severity="ERROR",
            )
            return None

    def set_overlay_size(self, handle: int, width_meters: float) -> bool:
        """
        Set overlay size in meters.

        Args:
            handle: Overlay handle
            width_meters: Width in meters

        Returns:
            True if successful
        """
        if not self.is_initialized:
            return False

        try:
            self.overlay_interface.setOverlayWidthInMeters(handle, width_meters)
            logger.debug(f"Overlay {handle} size set to {width_meters}m")
            return True
        except Exception as e:
            ErrorHandler.handle(e, context=f"set_overlay_size_{handle}")
            return False

    def set_overlay_texture(self, handle: int, texture_id: int) -> bool:
        """
        Assign OpenGL texture to overlay.

        Args:
            handle: Overlay handle
            texture_id: OpenGL texture ID

        Returns:
            True if successful
        """
        if not self.is_initialized:
            return False

        try:
            texture = openvr.Texture_t()
            texture.handle = ctypes.c_void_p(texture_id)
            texture.eType = openvr.TextureType_OpenGL
            texture.eColorSpace = openvr.ColorSpace_Gamma

            self.overlay_interface.setOverlayTexture(handle, texture)
            logger.debug(f"Texture {texture_id} assigned to overlay {handle}")
            return True
        except Exception as e:
            ErrorHandler.handle(
                e,
                context=f"set_overlay_texture_{handle}",
                severity="WARNING",
            )
            return False

    def set_overlay_transform(self, handle: int, matrix: np.ndarray) -> bool:
        """
        Set overlay position/rotation via transformation matrix.

        Args:
            handle: Overlay handle
            matrix: 4x4 transformation matrix

        Returns:
            True if successful
        """
        if not self.is_initialized:
            return False

        try:
            mat34 = openvr.HmdMatrix34_t()
            for r in range(3):
                for c in range(4):
                    mat34.m[r][c] = float(matrix[r][c])

            self.overlay_interface.setOverlayTransformAbsolute(
                handle,
                openvr.TrackingUniverseStanding,
                mat34,
            )
            return True
        except Exception as e:
            ErrorHandler.handle(e, context=f"set_overlay_transform_{handle}")
            return False

    def set_overlay_visibility(self, handle: int, visible: bool) -> bool:
        """
        Show or hide an overlay.

        Args:
            handle: Overlay handle
            visible: Visibility state

        Returns:
            True if successful
        """
        if not self.is_initialized:
            return False

        try:
            if visible:
                self.overlay_interface.showOverlay(handle)
            else:
                self.overlay_interface.hideOverlay(handle)
            logger.debug(f"Overlay {handle} visibility: {visible}")
            return True
        except Exception as e:
            ErrorHandler.handle(
                e,
                context=f"set_overlay_visibility_{handle}",
            )
            return False

    # ═══════════════════════════════════════════════════════════════════════════════
    # Pose Tracking
    # ═══════════════════════════════════════════════════════════════════════════════

    def get_head_pose(self) -> Optional[np.ndarray]:
        """
        Get current head (HMD) position and rotation.

        Returns:
            4x4 transformation matrix or None if unavailable
        """
        if not self.is_initialized or not self.vr_system:
            return None

        try:
            poses = np.zeros(1, dtype=openvr.TrackedDevicePose_t)
            poses = self.vr_system.getDeviceToAbsoluteTrackingPose(
                openvr.TrackingUniverseStanding, 0.0, poses
            )

            if poses.size > 0 and poses[0].bPoseIsValid:
                return mat34_to_numpy(poses[0].mDeviceToAbsoluteTracking)

            return None
        except Exception as e:
            ErrorHandler.handle(e, context="get_head_pose", severity="WARNING")
            return None

    def get_controller_poses(self) -> dict:
        """
        Get poses of all tracked controllers.

        Returns:
            Dict mapping device index to 4x4 transformation matrix
        """
        if not self.is_initialized or not self.vr_system:
            return {}

        controllers = {}
        try:
            poses = np.zeros(
                openvr.k_unMaxTrackedDeviceCount,
                dtype=openvr.TrackedDevicePose_t,
            )
            poses = self.vr_system.getDeviceToAbsoluteTrackingPose(
                openvr.TrackingUniverseStanding, 0.0, poses
            )

            for i, pose in enumerate(poses):
                if pose.bPoseIsValid:
                    device_class = self.vr_system.getTrackedDeviceClass(i)
                    if device_class == openvr.TrackedDeviceClass_Controller:
                        controllers[i] = mat34_to_numpy(pose.mDeviceToAbsoluteTracking)

            return controllers
        except Exception as e:
            ErrorHandler.handle(e, context="get_controller_poses", severity="WARNING")
            return {}

    # ═══════════════════════════════════════════════════════════════════════════════
    # Cleanup
    # ═══════════════════════════════════════════════════════════════════════════════

    def shutdown(self) -> None:
        """Clean up OpenVR resources."""
        try:
            if self.is_initialized:
                openvr.shutdown()
                self.is_initialized = False
                logger.info("OpenVR shutdown complete")
        except Exception as e:
            ErrorHandler.handle(e, context="vr_shutdown", severity="WARNING")

    def __del__(self):
        """Ensure cleanup on garbage collection."""
        self.shutdown()
