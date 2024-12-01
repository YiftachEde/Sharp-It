from moviepy.editor import VideoFileClip, concatenate_videoclips

# Function to process video with specified loop logic
def process_video(input_path, output_path):
    try:
        # Load the video
        video = VideoFileClip(input_path)
        
        # Extract specific clips: 1s->end, 0->1s
        from_first_to_end = video.subclip(3, video.duration)  # From 1s to the end
        from_start_to_first = video.subclip(0, 3)            # From start to 1s
        
        # Concatenate to form the desired sequence: 1s->end->0->1s
        desired_sequence = concatenate_videoclips([from_first_to_end, from_start_to_first])
        
        # Trim to make exactly 4 seconds long
        final_video = desired_sequence.subclip(0, 4)
        
        # Save the final video
        final_video.write_videofile(output_path, codec="libx264")
        print(f"Video successfully saved to {output_path}")
    except Exception as e:
        print(f"Error processing video: {str(e)}")

# Input and output paths
input_path = '/Users/yiftachedelstain/Sharp-It/static/videos/ddpm_inversion/torq_beetl_shap_e.mp4' # Replace with your input video file path
output_path = '/Users/yiftachedelstain/Sharp-It/static/videos/ddpm_inversion/torq_beetl_shap_e_corrected.mp4'  # Replace with your desired output file path

# Process the video
process_video(input_path, output_path)