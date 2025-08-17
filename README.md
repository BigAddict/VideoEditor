# Video Branding Processor

An advanced automated video processing tool that adds professional branding to videos by splitting them into three segments (intro, middle, outro) and applying different logo overlays to each segment. Features hardware acceleration, quality optimization, and comprehensive configuration options.

## 🚀 Features

- **File Watcher**: Automatically detects and processes new videos added to the `input/` folder
- **Three-Segment Processing**: Splits videos into intro, middle, and outro segments based on configurable durations
- **Dual Logo System**: 
  - Intro/Outro: Both static logo (top-left) and animated logo (bottom-center)
  - Middle: Static logo only (top-left)
- **Hardware Acceleration**: GPU-accelerated encoding for faster processing
- **Quality Optimization**: Advanced FFmpeg settings for optimal output quality
- **Memory Management**: Intelligent memory usage monitoring and cleanup
- **Multiple Format Support**: Handles MP4, AVI, MOV, MKV, WMV, FLV, and WebM formats
- **Automated File Management**: Moves processed files to avoid reprocessing
- **Comprehensive Logging**: Detailed logs for monitoring and debugging
- **Retry Logic**: Automatic retry for failed processing attempts
- **Performance Monitoring**: Real-time memory and performance tracking

## 📋 Requirements

- Python 3.8+
- FFmpeg installed on your system
- NVIDIA GPU (optional, for hardware acceleration)
- Sufficient disk space for video processing

## 🛠️ Setup

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

### 3. Prepare Assets

Ensure you have the following files in the `assets/` folder:
- `static_logo.png` - Static logo image for top-left positioning (PNG with transparency)
- `video_logo.mp4` - Animated logo video for bottom-center positioning

### 4. Configure Settings

Edit `settings.json` to customize all aspects of video processing:

```json
{
    "video_processing": {
        "intro_duration": 3,
        "outro_duration": 3,
        "min_video_duration": 6,
        "max_concurrent_processes": 1,
        "temp_dir": "temp"
    },
    "logo_configuration": {
        "static_logo": {
            "height": 80,
            "position": [20, 20],
            "opacity": 1.0,
            "scale_factor": 1.0
        },
        "animated_logo": {
            "height": 100,
            "position": "center",
            "bottom_margin": 120,
            "opacity": 1.0,
            "scale_factor": 1.0
        }
    },
    "output_settings": {
        "video_codec": "libx264",
        "audio_codec": "aac",
        "preset": "medium",
        "crf": 23,
        "bitrate": null,
        "audio_bitrate": "128k",
        "fps": null,
        "resolution": null,
        "format": "mp4"
    },
    "quality_settings": {
        "enable_hardware_acceleration": false,
        "gpu_codec": "h264_nvenc",
        "threads": 0,
        "buffer_size": "2M",
        "maxrate": null,
        "bufsize": null
    },
    "performance_settings": {
        "memory_limit_mb": 2048,
        "enable_progress_bar": true,
        "cleanup_temp_files": true,
        "parallel_processing": false,
        "chunk_size_seconds": 30
    },
    "file_management": {
        "auto_delete_processed": false,
        "keep_original_audio": true,
        "backup_original": false,
        "output_naming": "timestamp",
        "max_output_files": 100
    },
    "advanced_settings": {
        "enable_debug_logging": false,
        "log_level": "INFO",
        "save_processing_logs": true,
        "validate_output": true,
        "retry_failed_processing": true,
        "max_retry_attempts": 3
    }
}
```

## 🎯 Usage

### Start the Processor

```bash
python main.py
```

The processor will:
1. Process any existing videos in the `input/` folder
2. Start watching for new video files
3. Automatically process new videos as they are added

### How It Works

1. **File Detection**: When a video is added to the `input/` folder, it's automatically detected
2. **Video Analysis**: The video is analyzed for duration, resolution, and FPS
3. **Segmentation**: The video is split into three segments:
   - **Intro**: First N seconds (configurable)
   - **Middle**: Everything between intro and outro
   - **Outro**: Last N seconds (configurable)
4. **Logo Application**:
   - Intro/Outro segments get both static and animated logos
   - Middle segment gets only the static logo
5. **Output**: Branded video is saved to the `output/` folder with timestamp
6. **Cleanup**: Original video is moved to the `processed/` folder

### Output Structure

```
VideoEditor/
├── input/           # Add videos here
├── output/          # Branded videos appear here
├── processed/       # Original videos moved here after processing
├── temp/            # Temporary processing files
├── assets/          # Logo files
├── main.py          # Main processor script
├── settings.json    # Configuration
├── requirements.txt # Python dependencies
├── .gitignore       # Git ignore rules
└── video_processor.log  # Processing logs
```

## ⚙️ Configuration Guide

### Video Processing Settings

| Setting | Description | Default | Range |
|---------|-------------|---------|-------|
| `intro_duration` | Duration of intro segment in seconds | 3 | 0-60 |
| `outro_duration` | Duration of outro segment in seconds | 3 | 0-60 |
| `min_video_duration` | Minimum video length to process | 6 | 1-300 |
| `max_concurrent_processes` | Maximum parallel processing | 1 | 1-8 |
| `temp_dir` | Directory for temporary files | "temp" | - |

### Logo Configuration

#### Static Logo
- `file`: Path to the static logo image (default: `assets/static_logo.png`)
- `height`: Logo height in pixels
- `position`: [x, y] coordinates from top-left
- `opacity`: Transparency level (0.0-1.0)
- `scale_factor`: Size multiplier

#### Animated Logo
- `file`: Path to the animated logo video (default: `assets/video_logo.mp4`)
- `height`: Logo height in pixels
- `position`: "center" or [x, y] coordinates
- `bottom_margin`: Distance from bottom edge
- `opacity`: Transparency level (0.0-1.0)

### Output Quality Settings

#### Video Codec Options
- `libx264`: Standard H.264 encoding (default)
- `h264_nvenc`: NVIDIA GPU acceleration
- `h264_qsv`: Intel Quick Sync acceleration
- `libx265`: H.265/HEVC encoding

#### Quality Parameters
- `crf`: Constant Rate Factor (18-28, lower = better quality)
- `preset`: Encoding speed (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
- `bitrate`: Target bitrate (e.g., "2M", "5000k")
- `audio_bitrate`: Audio bitrate (e.g., "128k", "256k")

### Performance Settings

#### Hardware Acceleration
```json
"quality_settings": {
    "enable_hardware_acceleration": true,
    "gpu_codec": "h264_nvenc"
}
```

#### Memory Management
```json
"performance_settings": {
    "memory_limit_mb": 4096,
    "cleanup_temp_files": true
}
```

### File Management

#### Output Naming
- `timestamp`: `video_branded_20241201_143022.mp4`
- `sequential`: `video_branded_001.mp4`
- `simple`: `video_branded.mp4`

## 🚀 Performance Optimization

### Hardware Acceleration

Enable GPU acceleration for faster processing:

```json
"quality_settings": {
    "enable_hardware_acceleration": true,
    "gpu_codec": "h264_nvenc"
}
```

**Supported GPU Codecs:**
- `h264_nvenc`: NVIDIA GPUs
- `h264_qsv`: Intel integrated graphics
- `h264_amf`: AMD GPUs

### Quality vs Speed Trade-offs

**Fast Processing:**
```json
"output_settings": {
    "preset": "ultrafast",
    "crf": 28
}
```

**High Quality:**
```json
"output_settings": {
    "preset": "slow",
    "crf": 18
}
```

**Balanced:**
```json
"output_settings": {
    "preset": "medium",
    "crf": 23
}
```

### Memory Optimization

```json
"performance_settings": {
    "memory_limit_mb": 2048,
    "cleanup_temp_files": true,
    "chunk_size_seconds": 30
}
```

## 📊 Monitoring and Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General processing information
- `WARNING`: Warning messages
- `ERROR`: Error messages

### Log File
All processing information is saved to `video_processor.log`:
- File detection events
- Processing progress
- Performance metrics
- Error messages
- Success confirmations

## 🔧 Troubleshooting

### Common Issues

1. **"Required asset not found"**
   - Ensure `static_logo.png` and `video_logo.mp4` exist in the `assets/` folder

2. **"Video too short"**
   - Videos must be longer than the combined intro + outro duration
   - Check `min_video_duration` setting

3. **Hardware acceleration fails**
   - Verify GPU drivers are installed
   - Check if your GPU supports the selected codec
   - Try different GPU codecs: `h264_nvenc`, `h264_qsv`, `h264_amf`

4. **High memory usage**
   - Reduce `memory_limit_mb` in settings
   - Enable `cleanup_temp_files`
   - Process smaller videos or reduce quality settings

5. **Slow processing**
   - Enable hardware acceleration
   - Use faster presets (`ultrafast`, `superfast`)
   - Increase `crf` value for faster encoding
   - Reduce video resolution

### Performance Tips

- **For large videos**: Use hardware acceleration and faster presets
- **For high quality**: Use slower presets and lower CRF values
- **For batch processing**: Increase `max_concurrent_processes` (if memory allows)
- **For limited storage**: Enable `cleanup_temp_files` and `auto_delete_processed`

### Debug Mode

Enable detailed logging for troubleshooting:

```json
"advanced_settings": {
    "enable_debug_logging": true,
    "log_level": "DEBUG"
}
```

## 🛑 Stopping the Processor

Press `Ctrl+C` to gracefully stop the file watcher and exit the program.

## Asset Preparation Utility

If your static logo is a JPEG with a white background, convert it to a transparent PNG matching the processor expectation using:

```bash
python remove_background.py assets/static_logo1.jpeg assets/static_logo.png
```

If no arguments are provided, the script defaults to converting `assets/static_logo1.jpeg` to `assets/static_logo.png`.

## 📈 Performance Benchmarks

Typical processing times (1080p video, 30 seconds):

| Configuration | Processing Time | Quality |
|---------------|----------------|---------|
| CPU (medium preset) | 2-3 minutes | Good |
| GPU (h264_nvenc) | 30-60 seconds | Good |
| CPU (ultrafast) | 1-2 minutes | Acceptable |
| GPU (high quality) | 1-2 minutes | Excellent |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs in `video_processor.log`
3. Verify your settings in `settings.json`
4. Ensure all dependencies are installed

## 🔄 Version History

- **v2.0**: Added comprehensive settings, hardware acceleration, performance optimizations
- **v1.0**: Basic video processing with file watcher
