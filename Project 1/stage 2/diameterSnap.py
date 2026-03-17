STANDARD_DIAMETERS = [
    0.25,   # 1/4"
    0.375,  # 3/8"
    0.5,    # 1/2"
    0.625,  # 5/8"
    0.75,   # 3/4"
    1.0,    # 1"
    1.25    # 1 1/4"
]


SNAP_RING_STANDARD_DIAMETER = [
    0.25,
    0.28125,
    0.3125,
    0.34375,
    0.375,
    0.40625,
    0.4375,
    0.46875,
    0.5,
    0.5625,
    0.59375,
    0.625,
    0.6875,
    0.75,
    0.78125,
    0.8125,
    0.84375,
    0.875,
    0.9375,
    0.984375,
    1.0,
    1.0625,
    1.125,
    1.1875,
    1.25,
    1.3125,
    1.375,
    1.4375,
    1.5,
    1.5625,
    1.625,
    1.6875,
    1.75,
    1.8125,
    1.875,
    1.96875,
    2.0,
    2.0625,
    2.125,
    2.15625,
    2.25,
    2.3125,
    2.375,
    2.4375,
    2.5,
    2.559,
    2.625,
    2.6875,
    2.75,
    2.875
]

def snap_diameter(d_required , type):
        
        ls = SNAP_RING_STANDARD_DIAMETER if type == "snapRing" else STANDARD_DIAMETERS
        for d_std in ls:
            if d_std >= d_required:
                return d_std
        raise ValueError("Required diameter exceeds available standard sizes.")


def snap_all_diameters(segments , type):

    
    changed = False
    for seg in segments.values():
        d_old = seg.d
        seg.d = snap_diameter(seg.d , type)

        if abs(seg.d - d_old) > 1e-9:
            changed = True
    return changed
