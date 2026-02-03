from enum import Enum
import pandas as pd
import matplotlib.pyplot as plt

from core.aruco.aruco_utils import aruco_process
import numpy as np


class MarkerRole(Enum):
    HIP_TEST = "hip_test"
    HIP_BASE = "hip_base"
    TIBIA = "tibia"
    SHOULDER_LEFT = "shoulder_left"
    SHOULDER_RIGHT = "shoulder_right"

class TrendetecT():

    def __init__(self, video_path: str = None):
        super().__init__()
        self.df = None
        self.angle_series = None
        self.video_path = video_path


    def process_video(self, *args, **kwargs):
        kwargs['progress_callback'].emit(10)
        self.df = self.detect_data(args[0], frame_step=3)

        kwargs['progress_callback'].emit(25)
        self.df = self.assign_marker_roles(self.df)

        kwargs['progress_callback'].emit(40)
        if not self.validate_detection(self.df):
            raise ValueError("Detección insuficiente para procesar la prueba.")

        kwargs['progress_callback'].emit(55)
        self.df = self.interpolate_missing(self.df)
        
        offset = self.compute_offset(self.df)
        print(f'offset: {offset}')
        
        kwargs['progress_callback'].emit(70)
        self.df = self.crop_test_window(self.df)
        
        kwargs['progress_callback'].emit(85)
        self.angle_series = self.compute_hip_angles(self.df)
        self.angle_series = self.substract_base_angle(self.angle_series,offset)
        
        kwargs['progress_callback'].emit(95)
        results_df = self.generate_results_table(self.angle_series)
        angle_plot = self.generate_angle_plot(self.angle_series)
        
        kwargs['progress_callback'].emit(100)
        
        return [results_df, angle_plot]
    

    def detect_data(self, video_path: str, frame_step: int) -> pd.DataFrame:
        """
        Detecta marcadores, valida detección y realiza interpolación.
        Devuelve un DataFrame listo para procesamiento.
        """

        # Process the video to detect ArUco markers
        return aruco_process(video_path, 'DICT_6X6_250', frame_step)
    
    
    def validate_detection(self, df: pd.DataFrame, max_allowed_gap: int = 5) -> bool:
        """
        Valida la detección de los marcadores de cadera.
        Verifica que no haya más de `max_allowed_gap` NaNs consecutivos en ninguna columna de cadera.

        Args:
            df (pd.DataFrame): DataFrame con columnas renombradas según roles anatómicos.
            max_allowed_gap (int): Máximo número de NaNs consecutivos permitidos por columna.

        Returns:
            bool: True si la detección es válida, False si no.
        """
        # Columnas a evaluar
        hip_columns = [
            f"{MarkerRole.HIP_BASE.value}_x",
            f"{MarkerRole.HIP_BASE.value}_y",
            f"{MarkerRole.HIP_TEST.value}_x",
            f"{MarkerRole.HIP_TEST.value}_y"
        ]

        for col in hip_columns:
            # Serie booleana: True si es NaN
            is_nan = df[col].isna()

            # Detectar secuencias consecutivas de NaNs
            max_consec = 0
            current = 0
            for val in is_nan:
                if val:
                    current += 1
                    max_consec = max(max_consec, current)
                else:
                    current = 0

            if max_consec > max_allowed_gap:
                return False  # Falla la validación

        return True  # Todo dentro del límite

        


    def interpolate_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Interpola datos faltantes en el DataFrame.
        """
        
        hip_cols = [
        f"{MarkerRole.HIP_BASE.value}_x",
        f"{MarkerRole.HIP_BASE.value}_y",
        f"{MarkerRole.HIP_TEST.value}_x",
        f"{MarkerRole.HIP_TEST.value}_y"
        ]

        # Separar las columnas a interpolar
        hips_df = df[hip_cols]

        # Interpolación polinómica solo en caderas
        interpolated_hips = hips_df.interpolate(method='polynomial', order=2)
        
        interpolated_hips = interpolated_hips.dropna()

        # Reemplazar las columnas originales por las interpoladas
        df[hip_cols] = interpolated_hips

        return df


    
    def assign_marker_roles(self, df: pd.DataFrame, n_frames: int = 10) -> pd.DataFrame:
        """
        Asigna roles anatómicos a los marcadores según su posición en los primeros N frames.
        Identifica el marcador de tibia como el más alto en Y, y la cadera test como la más cercana en X a la tibia.
        Renombra las columnas del DataFrame con los roles: hip_base, hip_test, tibia.
        """
        df_sample = df.head(n_frames)

        # Extraer columnas de posición
        x_cols = [col for col in df.columns if col.endswith('_x')]
        #y_cols = [col for col in df.columns if col.endswith('_y')]

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

        if not markers:
            raise ValueError("No se detectaron marcadores válidos en los primeros frames.")

        # Identificar tibia como el marcador con mayor Y
        tibia = max(markers, key=lambda m: m['y'])
        hips = [m for m in markers if m != tibia]

        # Comparar distancia en X con tibia
        hip_test = min(hips, key=lambda m: abs(m['x'] - tibia['x']))
        hip_base = [m for m in hips if m != hip_test][0]

        # Renombrar columnas
        rename_map = {
            hip_base['x_col']: f'{MarkerRole.HIP_BASE.value}_x',
            hip_base['y_col']: f'{MarkerRole.HIP_BASE.value}_y',
            hip_test['x_col']: f'{MarkerRole.HIP_TEST.value}_x',
            hip_test['y_col']: f'{MarkerRole.HIP_TEST.value}_y',
            tibia['x_col']: f'{MarkerRole.TIBIA.value}_x',
            tibia['y_col']: f'{MarkerRole.TIBIA.value}_y'
        }

        df = df.rename(columns=rename_map)
        return df

    
    def compute_offset(self, df: pd.DataFrame) -> float:
        dx = df["hip_test_x"].iloc[0] - df["hip_base_x"].iloc[0]
        dy = df["hip_test_y"].iloc[0] - df["hip_base_y"].iloc[0]

        # inclinación respecto a la horizontal
        slope = dy / dx
        angle_deg = np.degrees(np.arctan(slope))
        return angle_deg
    
    
    def substract_base_angle(self, angles: pd.Series, offset:float) -> pd.Series:
        result = angles - offset
        return result


    def crop_test_window(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Recorta el DataFrame para quedarse solo con el período activo de la prueba.
        """
        nan_windows = self.get_nan_windows(df)
        nan_windows = self.collapse_detection_errors(nan_windows, min_len=5)
        
        # recortar el dataframe
        cropped_df = self.extract_test_segment(df, nan_windows)
        
        return cropped_df


    def compute_hip_angles(self, df: pd.DataFrame) -> pd.Series:
        """
        Calcula el ángulo de cadera por frame. Devuelve una Serie temporal.
        """
        angles = []
        for _, row in df.iterrows():
            dx = row["hip_test_x"] - row["hip_base_x"]
            dy = row["hip_test_y"] - row["hip_base_y"]   # invertimos signo (imagen Y hacia abajo)

            # inclinación respecto a la horizontal
            slope = dy / dx
            angle_deg = np.degrees(np.arctan(slope))

            angles.append(angle_deg)
        
        return pd.Series(angles, index=df["time"], name="hip_angle")


    def generate_results_table(self, angle_series: pd.Series) -> pd.DataFrame:
        """
        Genera un DataFrame resumen con métricas clave del ángulo.
        """
        # Filtrar valores válidos
        valid_angles = angle_series.dropna()

        # Métricas clave
        max_angle = valid_angles.max()
        max_time = valid_angles.idxmax()

        min_angle = valid_angles.min()
        min_time = valid_angles.idxmin()

        mean_angle = valid_angles.mean()

        # Duración de la prueba
        start_time = valid_angles.index.min()
        end_time = valid_angles.index.max()
        duration = end_time - start_time

        # Construcción del DataFrame resumen
        summary_df = pd.DataFrame({
            'Métrica': ['Ángulo máximo', 'Ángulo mínimo', 'Ángulo promedio', 'Duración'],
            'Valor': [max_angle, min_angle, mean_angle, duration],
            'Momento': [max_time, min_time, None, None]
        })

        return summary_df



    def generate_angle_plot(self, angle_series: pd.Series) -> plt.Figure:
        """
        Genera un gráfico de evolución del ángulo de cadera.
        """
        fig, ax = plt.subplots()

        # Plot the angle series
        ax.plot(angle_series.index, angle_series.values, label='Hip Angle', color='royalblue', linewidth=2)

        # Axis labels and title
        ax.set_xlabel("Tiempo (seg)")
        ax.set_ylabel("Angulo (°)")
        ax.set_title("Evolución del ángulo de cadera durante la prueba")

        # Grid and legend
        ax.grid(True, linestyle='--', alpha=0.5)
        #ax.legend(loc='upper right')

        # Optional: horizontal line at 0° for reference
        ax.axhline(0, color='gray', linestyle=':', linewidth=1)

        # Tight layout for better spacing
        fig.tight_layout()

        return fig

    
    def save_results(self, file_path: str):
        if self.angle_series is not None:
            self.angle_series.to_csv(file_path, index=False)
        else:
            raise ValueError("No hay datos para guardar. Procesa un video primero.")
    
    
    def load_results(self, file_path: str) -> pd.Series:
        self.angle_series = pd.read_csv(file_path)
        if self.angle_series is None:
            return None
        
        if self.angle_series.shape[1] > 1 :
            return None
        
        self.angle_series = self.angle_series.squeeze()
        
        results_df = self.generate_results_table(self.angle_series)
        angle_plot = self.generate_angle_plot(self.angle_series)
        
        return [results_df, angle_plot]
            
    
    
    def get_nan_windows(self, df: pd.DataFrame) -> pd.DataFrame:
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
        (change_indices)
        change_times = change_times = df.loc[state_changes, 'time'].to_list()
        change_states = is_nan[state_changes].to_list()

        # Construir el DataFrame
        result_df = pd.DataFrame({
            'index': change_indices,
            'time': change_times,
            'state': change_states
        })

        return result_df
    
    
    def collapse_detection_errors(self, change_df: pd.DataFrame, min_len: int = 5) -> pd.DataFrame:
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
    
    def extract_test_segment(self, df: pd.DataFrame, window_df: pd.DataFrame) -> pd.DataFrame:
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