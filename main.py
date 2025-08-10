import os
import json
import time
import logging
import shutil
import psutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import threading
from datetime import datetime
import gc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('video_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.settings = self.load_settings()
        self.setup_directories()
        self.check_assets()
        self.processed_files = set()
        self.processing_lock = threading.Lock()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging based on settings."""
        log_level = getattr(logging, self.settings.get('advanced_settings', {}).get('log_level', 'INFO'))
        logger.setLevel(log_level)
        
    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        directories = ["input", "output", "processed"]
        temp_dir = self.settings.get('video_processing', {}).get('temp_dir', 'temp')
        if temp_dir:
            directories.append(temp_dir)
            
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory '{directory}' ready")
    
    def check_assets(self):
        """Verify that required assets exist."""
        required_assets = [
            "assets/static_logo.jpeg",
            "assets/video_logo.mp4"
        ]
        
        for asset in required_assets:
            if not os.path.exists(asset):
                raise FileNotFoundError(f"Required asset not found: {asset}")
        logger.info("All required assets found")
    
    def load_settings(self) -> dict:
        """Load and validate settings from settings.json."""
        try:
            with open("settings.json", "r") as f:
                settings = json.load(f)
            
            # Validate required settings
            video_processing = settings.get('video_processing', {})
            required_keys = ["intro_duration", "outro_duration"]
            for key in required_keys:
                if key not in video_processing:
                    raise ValueError(f"Missing required setting: video_processing.{key}")
                if not isinstance(video_processing[key], (int, float)) or video_processing[key] < 0:
                    raise ValueError(f"Invalid value for video_processing.{key}: must be a positive number")
            
            logger.info(f"Settings loaded successfully")
            return settings
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            raise
    
    def check_memory_usage(self):
        """Check if memory usage is within limits."""
        memory_limit = self.settings.get('performance_settings', {}).get('memory_limit_mb', 2048)
        current_memory = psutil.virtual_memory().percent
        if current_memory > 90:  # If system memory usage > 90%
            logger.warning(f"High memory usage detected: {current_memory}%")
            gc.collect()  # Force garbage collection
    
    def get_video_info(self, video_path: str) -> dict:
        """Get video metadata."""
        try:
            clip = VideoFileClip(video_path)
            info = {
                'duration': clip.duration,
                'size': clip.size,
                'fps': clip.fps,
                'audio': clip.audio is not None
            }
            clip.close()
            return info
        except Exception as e:
            logger.error(f"Failed to get video info for {video_path}: {e}")
            raise
    
    def is_video_file(self, file_path: str) -> bool:
        """Check if file is a supported video format."""
        video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        return Path(file_path).suffix.lower() in video_extensions
    
    def get_output_filename(self, video_path: str) -> str:
        """Generate output filename based on settings."""
        input_filename = Path(video_path).stem
        naming_convention = self.settings.get('file_management', {}).get('output_naming', 'timestamp')
        
        if naming_convention == 'timestamp':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return f"output/{input_filename}_branded_{timestamp}.mp4"
        elif naming_convention == 'sequential':
            # Find next available number
            counter = 1
            while os.path.exists(f"output/{input_filename}_branded_{counter:03d}.mp4"):
                counter += 1
            return f"output/{input_filename}_branded_{counter:03d}.mp4"
        else:
            return f"output/{input_filename}_branded.mp4"
    
    def cleanup_temp_files(self):
        """Clean up temporary files if enabled."""
        if self.settings.get('performance_settings', {}).get('cleanup_temp_files', True):
            temp_dir = self.settings.get('video_processing', {}).get('temp_dir', 'temp')
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                    os.makedirs(temp_dir, exist_ok=True)
                    logger.debug("Temporary files cleaned up")
                except Exception as e:
                    logger.warning(f"Failed to cleanup temp files: {e}")
    
    def process_video(self, video_path: str) -> bool:
        """Process a single video file with enhanced settings."""
        with self.processing_lock:
            try:
                logger.info(f"Starting processing of: {video_path}")
                self.check_memory_usage()
                
                # Get video info
                video_info = self.get_video_info(video_path)
                logger.info(f"Video info: duration={video_info['duration']:.2f}s, size={video_info['size']}, fps={video_info['fps']}")
                
                # Check if video is long enough for the segments
                video_processing = self.settings.get('video_processing', {})
                total_duration = video_processing["intro_duration"] + video_processing["outro_duration"]
                min_duration = video_processing.get('min_video_duration', 6)
                
                if video_info['duration'] <= total_duration:
                    logger.warning(f"Video too short ({video_info['duration']:.2f}s) for segments (need >{total_duration}s). Skipping.")
                    return False
                
                if video_info['duration'] < min_duration:
                    logger.warning(f"Video too short ({video_info['duration']:.2f}s) for minimum duration ({min_duration}s). Skipping.")
                    return False
                
                # Load main video
                main_video = VideoFileClip(video_path)
                
                # Prepare logos with enhanced settings
                logo_config = self.settings.get('logo_configuration', {})
                static_config = logo_config.get('static_logo', {})
                animated_config = logo_config.get('animated_logo', {})
                
                static_logo = (
                    ImageClip("assets/static_logo.jpeg")
                    .resized(height=static_config.get('height', 80))
                    .with_position(static_config.get('position', [20, 20]))
                )
                
                if static_config.get('opacity', 1.0) != 1.0:
                    static_logo = static_logo.with_opacity(static_config.get('opacity', 1.0))
                
                animated_logo = (
                    VideoFileClip("assets/video_logo.mp4")
                    .resized(height=animated_config.get('height', 100))
                )
                
                # Position animated logo
                if animated_config.get('position') == 'center':
                    bottom_margin = animated_config.get('bottom_margin', 120)
                    animated_logo = animated_logo.with_position(("center", video_info['size'][1] - bottom_margin))
                else:
                    animated_logo = animated_logo.with_position(animated_config.get('position', ("center", "bottom")))
                
                if animated_config.get('opacity', 1.0) != 1.0:
                    animated_logo = animated_logo.with_opacity(animated_config.get('opacity', 1.0))
                
                # Split into segments
                intro_duration = video_processing["intro_duration"]
                outro_duration = video_processing["outro_duration"]
                middle_start = intro_duration
                middle_end = video_info['duration'] - outro_duration
                
                intro_clip = main_video.subclipped(0, intro_duration)
                middle_clip = main_video.subclipped(middle_start, middle_end)
                outro_clip = main_video.subclipped(middle_end, video_info['duration'])
                
                logger.info(f"Segments: intro={intro_duration}s, middle={middle_clip.duration:.2f}s, outro={outro_duration}s")
                
                # Apply logos to segments
                intro_with_logos = CompositeVideoClip([
                    intro_clip,
                    static_logo.with_duration(intro_duration),
                    animated_logo.with_duration(intro_duration)
                ])
                
                middle_with_logo = CompositeVideoClip([
                    middle_clip,
                    static_logo.with_duration(middle_clip.duration)
                ])
                
                outro_with_logos = CompositeVideoClip([
                    outro_clip,
                    static_logo.with_duration(outro_duration),
                    animated_logo.with_duration(outro_duration)
                ])
                
                # Concatenate segments
                final = concatenate_videoclips([intro_with_logos, middle_with_logo, outro_with_logos])
                
                # Generate output filename
                output_filename = self.get_output_filename(video_path)
                
                # Prepare output settings
                output_settings = self.settings.get('output_settings', {})
                quality_settings = self.settings.get('quality_settings', {})
                
                # Build FFmpeg parameters
                ffmpeg_params = {
                    'codec': output_settings.get('video_codec', 'libx264'),
                    'audio_codec': output_settings.get('audio_codec', 'aac'),
                    'fps': output_settings.get('fps') or video_info['fps']
                }
                
                # Add quality settings using ffmpeg_params for advanced options
                ffmpeg_extra_args = []
                
                if output_settings.get('preset'):
                    ffmpeg_extra_args.extend(['-preset', output_settings['preset']])
                if output_settings.get('crf'):
                    ffmpeg_extra_args.extend(['-crf', str(output_settings['crf'])])
                if output_settings.get('bitrate'):
                    ffmpeg_extra_args.extend(['-b:v', output_settings['bitrate']])
                if output_settings.get('audio_bitrate'):
                    ffmpeg_extra_args.extend(['-b:a', output_settings['audio_bitrate']])
                if quality_settings.get('threads'):
                    ffmpeg_extra_args.extend(['-threads', str(quality_settings['threads'])])
                if quality_settings.get('buffer_size'):
                    ffmpeg_extra_args.extend(['-bufsize', quality_settings['buffer_size']])
                
                # Hardware acceleration
                if quality_settings.get('enable_hardware_acceleration', False):
                    ffmpeg_params['codec'] = quality_settings.get('gpu_codec', 'h264_nvenc')
                
                # Add extra FFmpeg arguments if any
                if ffmpeg_extra_args:
                    ffmpeg_params['ffmpeg_params'] = ffmpeg_extra_args
                
                # Export final video
                logger.info(f"Exporting to: {output_filename}")
                final.write_videofile(
                    output_filename,
                    **ffmpeg_params
                )
                
                # Cleanup
                main_video.close()
                final.close()
                static_logo.close()
                animated_logo.close()
                
                # Validate output if enabled
                if self.settings.get('advanced_settings', {}).get('validate_output', True):
                    if os.path.exists(output_filename) and os.path.getsize(output_filename) > 0:
                        logger.info("Output validation successful")
                    else:
                        raise Exception("Output validation failed - file is empty or missing")
                
                # Move processed file
                processed_path = f"processed/{Path(video_path).name}"
                os.rename(video_path, processed_path)
                
                # Cleanup temp files
                self.cleanup_temp_files()
                
                logger.info(f"Successfully processed: {video_path} -> {output_filename}")
                return True
                
            except Exception as e:
                logger.error(f"Failed to process {video_path}: {e}")
                
                # Retry logic
                retry_settings = self.settings.get('advanced_settings', {})
                if retry_settings.get('retry_failed_processing', True):
                    max_attempts = retry_settings.get('max_retry_attempts', 3)
                    # Implementation for retry logic would go here
                    logger.info(f"Retry logic available (max {max_attempts} attempts)")
                
                return False
    
    def process_existing_videos(self):
        """Process any existing videos in the input folder."""
        input_dir = Path("input")
        video_files = [f for f in input_dir.iterdir() if f.is_file() and self.is_video_file(str(f))]
        
        if video_files:
            logger.info(f"Found {len(video_files)} existing video(s) to process")
            for video_file in video_files:
                if str(video_file) not in self.processed_files:
                    self.process_video(str(video_file))
                    self.processed_files.add(str(video_file))
        else:
            logger.info("No existing videos found in input folder")

class VideoFileHandler(FileSystemEventHandler):
    def __init__(self, processor: VideoProcessor):
        self.processor = processor
    
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if self.processor.is_video_file(file_path):
                logger.info(f"New video file detected: {file_path}")
                # Wait a bit to ensure file is fully written
                time.sleep(2)
                if file_path not in self.processor.processed_files:
                    self.processor.process_video(file_path)
                    self.processor.processed_files.add(file_path)

def main():
    """Main function to run the video processor with file watching."""
    try:
        # Initialize processor
        processor = VideoProcessor()
        
        # Process any existing videos
        processor.process_existing_videos()
        
        # Set up file watcher
        event_handler = VideoFileHandler(processor)
        observer = Observer()
        observer.schedule(event_handler, path="input", recursive=False)
        observer.start()
        
        logger.info("Video processor started. Watching for new videos in 'input' folder...")
        logger.info("Press Ctrl+C to stop")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            logger.info("Stopping video processor...")
        
        observer.join()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    main()