ffmpeg -i output.avi -vf reverse  -c:v libx264 -r 24 -pix_fmt yuv420p reversed.mp4
