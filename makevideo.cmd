rem -pattern_type sequence
ffmpeg -r 24  -start_number 1 -i "output/%%d.png" -c:v libx264 -r 24 -pix_fmt yuv420p  output.avi

