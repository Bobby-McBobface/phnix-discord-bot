import time

R, G, B = 256 * 256, 256, 1

def colour_int_to_tuple(colour:int) -> tuple:
    """Takes a 24-bit colour integer and turns it into (R, G, B) format."""
    # Mask out only the relavent bits and shift them into place
    r = (colour & 0xff0000) >> 16
    g = (colour & 0xff00) >> 8
    b = (colour & 0xff)
    return (r, g, b)


def colour_tuple_to_int(colour:tuple) -> int:
    """Takes a colour in (R, G, B) format and combines it into a single 24-bit integer format."""
    return R*colour[0] + G*colour[1] + B*colour[2]


def RGB_to_HSL(r:int, g:int, b:int) -> tuple:
    """Formula adapted from https://www.rapidtables.com/convert/color/rgb-to-hsl.html"""
    # put RGB into 0..1 range
    r = r / 255
    g = g / 255
    b = b / 255
    
    cmax = max(r, g, b)
    cmin = min(r, g, b)
    delta = cmax - cmin
    
    if delta == 0: hue = 0
    elif cmax == r: hue = 60*(((g - b)/delta) % 6)
    elif cmax == g: hue = 60*(((b - r)/delta) + 2)
    elif cmax == b: hue = 60*(((r - g)/delta) + 4)
    
    lightness = (cmax + cmin) / 2
    
    saturation = 0 if delta == 0 \
    else delta / (1 - abs(2*lightness - 1))
    
    return (hue, saturation, lightness)


def HSL_to_RGB(hsl_tuple) -> int:
    """Formula adapted from https://www.rapidtables.com/convert/color/hsl-to-rgb.html"""
    H, S, L = hsl_tuple
    C = (1 - abs(2*L - 1)) * S
    X = C * (1 - abs((H / 60) % 2 - 1))
    m = L - C/2
    
    if     0 <= H <  60: r, g, b = (C, X, 0)
    elif  60 <= H < 120: r, g, b = (X, C, 0)
    elif 120 <= H < 180: r, g, b = (0, C, X)
    elif 180 <= H < 240: r, g, b = (0, X, C) 
    elif 240 <= H < 300: r, g, b = (X, 0, C)
    elif 300 <= H < 360: r, g, b = (C, 0, X) 
    
    rgb = (round((r+m)*255), round((g+m)*255), round((b+m)*255))
    
    return colour_tuple_to_int(rgb)


def temporal_colour_gradient(start_time, end_time, start_colour, end_colour) -> int:
    """Returns a colour based off a starting time and colour, and ending time and colour, and the current time."""
    
    now_time = time.time() # What time is it right now?
    
    # What fraction of the time are we up to?
    time_fraction = (now_time - start_time) / (end_time - start_time)
    
    # Get R, G, and B values
    if isinstance(start_colour, int):
        start_r, start_g, start_b = colour_int_to_tuple(start_colour)
    else:
        start_r, start_g, start_b = start_colour # Assume it is a tuple or something
    
    if isinstance(end_colour, int):
        end_r, end_g, end_b = colour_int_to_tuple(end_colour)
    else:
        end_r, end_g, end_b = end_colour # Assume it is a tuple or something
    
    # Convert to HSL to make a nicer gradient
    start_hsl = RGB_to_HSL(start_r, start_g, start_b)
    end_hsl = RGB_to_HSL(end_r, end_g, end_b)
    
    # Lerp with our time_fraction
    now_hsl = (
        start_hsl[0] + (end_hsl[0] - start_hsl[0]) * time_fraction,
        start_hsl[1] + (end_hsl[1] - start_hsl[1]) * time_fraction,
        start_hsl[2] + (end_hsl[2] - start_hsl[2]) * time_fraction
    )
    
    # Convert back to a colour int that discord will accept
    return HSL_to_RGB(now_hsl)