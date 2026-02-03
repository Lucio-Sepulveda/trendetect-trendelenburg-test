from core.aruco.aruco_utils import generate_aruco_markers
from core.aruco.aruco_utils import aruco_process
from core.tools import math_tools

import cv2
import pandas as pd


def generate_markers():
    # Specify the folder path where the markers will be saved
    folder_path = 'data/aruco_markers/400x400'

    # Generate and save the markers
    generate_aruco_markers(dict_info='DICT_6X6_250', marker_count=4, marker_size=400, folder_path=folder_path)


def detect_markers():
    
    image = cv2.imread('data/photos/markers_1.jpg')
    
    detected = cv2.aruco.detectMarkers(image, cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250))
    
    output_image = cv2.aruco.drawDetectedMarkers(image, detected[0], detected[1])
    cv2.imwrite('data/photos/markers_1_detected.jpg', output_image)
    

def process_video():
    # Specify the video path and frame step
    video_path = 'data/videos/sample_3.mp4'
    frame_step = 2

    # Process the video to detect ArUco markers
    info = aruco_process(video_path, 'DICT_6X6_250', frame_step)
    # info = info.interpolate(method='polynomial', order=2)
    # info = info.dropna()
    
    info.to_csv('data/processed_info/sample_3_output.csv', index=True)
    

def process_info():
    info = pd.read_csv('data/processed_info/sample_3_output.csv')
    
    info = assign_marker_roles_by_position(info, n_frames=10)
    nan_windows = get_nan_windows(info)
    nan_windows = collapse_detection_errors(nan_windows, min_len=5)
    result = crop_test_window(info, nan_windows)
    result.to_csv('data/processed_info/result.csv', index=False)


def assign_marker_roles_by_position(df: pd.DataFrame, n_frames: int = 10) -> pd.DataFrame:
    """
    Asigna roles anatómicos a los marcadores según su posición en los primeros N frames.
    Identifica el marcador de tibia como el más alto en Y, y la cadera test como la más cercana en X a la tibia.
    Renombra las columnas del DataFrame con los roles: hip_base, hip_test, tibia.
    """
    df_sample = df.head(n_frames)

    # Extraer columnas de posición
    x_cols = [col for col in df.columns if col.endswith('_x')]
    y_cols = [col for col in df.columns if col.endswith('_y')]

    # Construir lista de marcadores con su primera posición válida
    markers = []
    for x_col in x_cols:
        y_col = x_col.replace('_x', '_y')
        x_vals = df_sample[x_col].dropna()
        y_vals = df_sample[y_col].dropna()

        if not x_vals.empty and not y_vals.empty:
            x = x_vals.iloc[0]
            y = y_vals.iloc[0]
            marker_id = x_col.split('_')[1]
            markers.append({'id': marker_id, 'x': x, 'y': y, 'x_col': x_col, 'y_col': y_col})

    if len(markers) != 3:
        raise ValueError("No se detectaron 3 marcadores válidos en los primeros frames.")

    # Identificar tibia como el marcador con mayor Y
    tibia = max(markers, key=lambda m: m['y'])
    hips = [m for m in markers if m != tibia]

    # Comparar distancia en X con tibia
    hip_test = min(hips, key=lambda m: abs(m['x'] - tibia['x']))
    hip_base = [m for m in hips if m != hip_test][0]

    # Renombrar columnas
    rename_map = {
        hip_base['x_col']: 'hip_base_x',
        hip_base['y_col']: 'hip_base_y',
        hip_test['x_col']: 'hip_test_x',
        hip_test['y_col']: 'hip_test_y',
        tibia['x_col']: 'tibia_x',
        tibia['y_col']: 'tibia_y'
    }

    df = df.rename(columns=rename_map)
    return df


def collapse_detection_errors(change_df: pd.DataFrame, min_len: int = 5) -> pd.DataFrame:
    """
    Removes short 'True' windows (non-detection) that are likely due to detection errors,
    and merges adjacent windows with the same state.

    Args:
        change_df (pd.DataFrame): DataFrame with columns ['index', 'time', 'state']
        min_len (int): Minimum number of indices a 'True' window must last to be considered valid

    Returns:
        pd.DataFrame: Cleaned DataFrame with consolidated windows
    """
    collapsed = []
    i = 0

    while i < len(change_df) - 1:
        current = change_df.iloc[i]
        next_ = change_df.iloc[i + 1]
        duration = next_['index'] - current['index']

        # If current is a short True window, skip both current and next
        if current['state'] and duration < min_len:
            i += 2
            continue

        # If last added state is same as current, replace it (merge)
        if collapsed and collapsed[-1]['state'] == current['state']:
            collapsed[-1] = current
        else:
            collapsed.append(current)

        i += 1

    # Handle last row if not already merged
    if i == len(change_df) - 1:
        last = change_df.iloc[-1]
        if not collapsed or collapsed[-1]['state'] != last['state']:
            collapsed.append(last)

    return pd.DataFrame(collapsed).reset_index(drop=True)


def get_nan_windows(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un DataFrame que indica los puntos de cambio de estado de detección en la columna dada.

    Args:
        df (pd.DataFrame): DataFrame con índice temporal.
        column (str): Nombre de la columna a analizar (ej. 'tibia_x').

    Returns:
        pd.DataFrame: DataFrame con columnas:
            - 'index': índice numérico donde ocurre el cambio
            - 'time': valor del índice (tiempo) donde ocurre el cambio
            - 'state': True si no hay detección (NaN), False si hay detección
    """
    column = 'tibia_x'
    # Serie booleana: True si hay NaN (no se detecta)
    is_nan = df[column].isna()

    # Detectar cambios de estado
    state_changes = is_nan != is_nan.shift(1)

    # Extraer índices numéricos y tiempos
    change_indices = df.index[state_changes].to_list()
    change_times = change_times = df.loc[state_changes, 'time'].to_list()
    change_states = is_nan[state_changes].to_list()

    # Construir el DataFrame
    result_df = pd.DataFrame({
        'index': change_indices,
        'time': change_times,
        'state': change_states
    })

    return result_df


def crop_test_window(df: pd.DataFrame, window_df: pd.DataFrame) -> pd.DataFrame:
    """
    Recorta el DataFrame original según la ventana de prueba indicada en window_df.

    Args:
        df (pd.DataFrame): DataFrame completo con datos de marcadores.
        window_df (pd.DataFrame): DataFrame con columnas ['index', 'time', 'state'],
                                  indicando los cambios de estado (True = ventana de prueba).

    Returns:
        pd.DataFrame: DataFrame recortado a la ventana principal de prueba.
    """
    # Filtrar solo las ventanas True
    true_windows = window_df[window_df['state'] == True]

    if true_windows.empty:
        raise ValueError("No se detectó ninguna ventana de prueba válida.")

    # Tomar la primera ventana True
    start_idx = true_windows.iloc[0]['index']
    try:
        end_idx = window_df.iloc[window_df[window_df['index'] == start_idx].index[0] + 1]['index']
    except IndexError:
        end_idx = df.index[-1]  # Si no hay cambio posterior, cortar hasta el final

    # Recortar el df original
    cropped_df = df.iloc[start_idx:end_idx + 1].reset_index(drop=True)
    return cropped_df





if __name__ == "__main__":
    #generate_markers()
    #detect_markers()
    
    #process_video()
    
    process_info()
    
    pass