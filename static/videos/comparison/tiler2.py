import os
from pathlib import Path
import cv2

# Paths to video files
video_files = [
    '/Users/yiftachedelstain/Sharp-It/static/videos/shap-editor/lamps/shap_e.mp4',
    '/Users/yiftachedelstain/Sharp-It/static/videos/shap-editor/lamps/santa_lamp.mp4',
'/Users/yiftachedelstain/Sharp-It/static/videos/shap-editor/lamps/santa_lamp_sharp_it.mp4'
]

# Output settings
temp_dir = Path("/Users/yiftachedelstain/Development/paper_obj/avocados/temp")
temp_dir.mkdir(exist_ok=True)
tile_cols, tile_rows = 3, 1
output_width, output_height = 960, 320
tile_width = output_width // tile_cols
tile_height = output_height // tile_rows
final_output_path = '/Users/yiftachedelstain/Sharp-It/static/videos/shap-editor/lamps/santa_lamps_comparison.mp4'

# Extract titles from video file names
titles = ['' for video_file in video_files]

# Function to resize videos and overlay titles using OpenCV
def process_and_resize(video_path, tile_width, tile_height, title):
    cap = cv2.VideoCapture(video_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0 or fps != fps:  # Check for invalid FPS values
        fps = 30  # Default FPS if not available
    out_path = str(temp_dir / f"{Path(video_path).stem}_tiled.mp4")
    out = cv2.VideoWriter(out_path, int(fourcc), fps, (tile_width, tile_height))

    # Set up font parameters
    font_scale = tile_height / 500  # Adjust as needed
    font_thickness = 2
    font = cv2.FONT_HERSHEY_SIMPLEX

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        resized_frame = cv2.resize(frame, (tile_width, tile_height))

        # Get text size
        text_size, _ = cv2.getTextSize(title, font, font_scale, font_thickness)
        text_width, text_height = text_size

        # Calculate position for top-left corner
        text_x = 10  # 10 pixels from the left edge
        text_y = text_height + 10  # 10 pixels from the top edge

        # Draw white background rectangle for better visibility
        cv2.rectangle(resized_frame, (text_x - 5, text_y - text_height - 5),
                      (text_x + text_width + 5, text_y + 5), (255, 255, 255), -1)

        # Put black text on the frame
        cv2.putText(resized_frame, title, (text_x, text_y), font, font_scale,
                    (0, 0, 0), font_thickness, cv2.LINE_AA)

        out.write(resized_frame)

    cap.release()
    out.release()
    return out_path

# Resize all videos and overlay titles using OpenCV
tiled_videos = [process_and_resize(video_file, tile_width, tile_height, titles[i]) for i, video_file in enumerate(video_files)]

# Construct FFmpeg filter_complex for tiling without titles
# Create horizontal stacks for each row
row_filters = []
for row in range(tile_rows):
    indices = [row * tile_cols + col for col in range(tile_cols)]
    inputs = ''.join([f"[{i}:v]" for i in indices])
    if tile_cols == 1:
        # Only one column, no need to hstack
        row_filters.append(f"{inputs}[row{row}]")
    else:
        row_filters.append(f"{inputs}hstack=inputs={tile_cols}[row{row}]")

# Stack the rows vertically
if tile_rows == 1:
    # Only one row, no need to vstack
    filter_complex = ';'.join(row_filters)
    output_label = '[row0]'
else:
    final_grid = ''.join([f"[row{row}]" for row in range(tile_rows)]) + f"vstack=inputs={tile_rows}[outv]"
    filter_complex = ';'.join(row_filters + [final_grid])
    output_label = '[outv]'

# Construct the FFmpeg command
ffmpeg_inputs = ' '.join([f"-i '{vid}'" for vid in tiled_videos])
ffmpeg_command = (
    f"ffmpeg {ffmpeg_inputs} -filter_complex \"{filter_complex}\" -map {output_label} "
    f"-c:v libx264 -preset fast -crf 18 '{final_output_path}'"
)

# Print the FFmpeg command for debugging
print("FFmpeg command:")
print(ffmpeg_command)

# Execute the command
os.system(ffmpeg_command)
print(f"Tiled video saved to: {final_output_path}")