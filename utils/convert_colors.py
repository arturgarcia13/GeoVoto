import matplotlib.colors as mcolors

def hex_to_rgb(hex_color):
    rgb = mcolors.to_rgb(hex_color)
    return [int(c * 255) for c in rgb] + [60] 
