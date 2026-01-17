"""
Mathematical Utilities Module.

Provides matrix transformations and other math operations.
"""

from typing import Any
import numpy as np
import openvr

from core.logger import get_logger

logger = get_logger("MathUtils")


def mat34_to_numpy(matrix: Any) -> np.ndarray:
    """
    Convert OpenVR HmdMatrix34 to NumPy array.

    Args:
        matrix: openvr.HmdMatrix34_t

    Returns:
        4x4 NumPy array with last row as [0, 0, 0, 1]
    """
    try:
        data = [[matrix.m[r][c] for c in range(4)] for r in range(3)]
        data.append([0, 0, 0, 1])
        return np.array(data)
    except Exception as e:
        logger.error(f"Failed to convert matrix to numpy: {e}")
        return np.identity(4)


def numpy_to_mat34(matrix: np.ndarray) -> Any:
    """
    Convert NumPy array to OpenVR HmdMatrix34.

    Args:
        matrix: 4x4 NumPy array

    Returns:
        openvr.HmdMatrix34_t
    """
    try:
        mat34 = openvr.HmdMatrix34_t()
        for r in range(3):
            for c in range(4):
                mat34.m[r][c] = float(matrix[r][c])
        return mat34
    except Exception as e:
        logger.error(f"Failed to convert numpy to matrix: {e}")
        return openvr.HmdMatrix34_t()


def get_distance(pos1: np.ndarray, pos2: np.ndarray) -> float:
    """
    Calculate Euclidean distance between two 3D positions.

    Args:
        pos1: Position 1 as [x, y, z]
        pos2: Position 2 as [x, y, z]

    Returns:
        Euclidean distance
    """
    return float(np.linalg.norm(pos2 - pos1))


def matrix_inverse(matrix: np.ndarray) -> np.ndarray:
    """
    Calculate matrix inverse with error handling.

    Args:
        matrix: Input matrix

    Returns:
        Inverted matrix or identity if singular
    """
    try:
        return np.linalg.inv(matrix)
    except np.linalg.LinAlgError:
        logger.warning("Singular matrix, returning identity")
        return np.identity(4)
