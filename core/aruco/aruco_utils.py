from cv2 import aruco
import cv2
import numpy as np
import pandas as pd


def generate_aruco_markers(dictionary_name, marker_size, marker_count, folder_path:str):
    """
    Generate ArUco markers and save them to the specified folder.

    Args:
        marker_info (MarkerInfo): The marker information object containing dictionary name, marker count, and size.
        folder_path (str): The path to the folder where the markers will be saved.
    """
    # Get the dictionary
    dictionary = get_aruco_dictionary(dictionary_name)
    # Generate and save each marker
    for i in range(marker_count):
        # Create the marker
        marker_image = aruco.generateImageMarker(dictionary, i, marker_size)
        # Save the marker image
        cv2.imwrite(f"{folder_path}/marker_{i}.png", marker_image)



def detect_aruco_markers(image, dictionary_name):
    """
    Detect ArUco markers in an image.

    Args:
        image (numpy.ndarray): The input image.
        marker_info (MarkerInfo): The marker information object containing dictionary name and marker size.

    Returns:
        tuple: A tuple containing the corners and ids of the detected markers.
    """
    # Detect markers
    dictionary = get_aruco_dictionary(dictionary_name)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(image, dictionary)
    return corners, ids



def aruco_process(video_path:str, dictionary_name, frame_step:int=0, include_steps=False):
    """
    Process a video file to detect ArUco markers.

    Args:
        video_path (str): The path to the video file.
        marker_info (MarkerInfo): The marker information object containing dictionary name and marker size.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"No se pudo abrir el video en {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_index = 0
    
    rows = []
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Saltar frames si se indicó
        if frame_step and (frame_index % (frame_step + 1)) != 0:
            if include_steps:
                time = frame_index / fps
                rows.append({'time': time})
            
            frame_index += 1
            continue
        
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)  # rotar a portrait
        corners, ids = detect_aruco_markers(frame, dictionary_name)
        
        time = frame_index / fps
        row = {'time': time}


        if ids is not None:
            for id_, corner in zip(ids.flatten(), corners):
                centro = np.mean(corner[0], axis=0)
                row[f"id_{int(id_)}_x"] = centro[0]
                row[f"id_{int(id_)}_y"] = centro[1]


        rows.append(row)
        frame_index += 1

    cap.release()
    outcome = pd.DataFrame(rows)
    #outcome.set_index('time', inplace=True)

    return outcome


def get_aruco_dictionary(dictionary_name: str):
    return cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary_name))