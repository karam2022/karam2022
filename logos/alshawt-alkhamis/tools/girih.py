"""A football (truncated icosahedron) dressed in Islamic star geometry via Hankin's polygons-in-contact method."""
import math, itertools

PHI = (1 + 5 ** 0.5) / 2


def norm(v):
    l = math.sqrt(sum(x * x for x in v)); return tuple(x / l for x in v)
def dot(a, b): return sum(x * y for x, y in zip(a, b))
def sub(a, b): return tuple(x - y for x, y in zip(a, b))
def add(a, b): return tuple(x + y for x, y in zip(a, b))
def mul(a, k): return tuple(x * k for x in a)
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def even_perms(v):
    x, y, z = v
    return [(x, y, z), (y, z, x), (z, x, y)]


def signed(v):
    out = set()
    for s in itertools.product(*[(1, -1) if c else (1,) for c in v]):
        out.add(tuple(c * k for c, k in zip(v, s)))
    return out


def truncated_icosahedron():
    base = [(0, 1, 3 * PHI), (1, 2 + PHI, 2 * PHI), (PHI, 2, 2 * PHI + 1)]
    verts = set()
    for b in base:
        for p in even_perms(b):
            for s in signed(p):
                verts.add(tuple(round(c, 9) for c in s))
    verts = list(verts); assert len(verts) == 60
    # face normals: icosahedron vertices → pentagons, dodecahedron vertices → hexagons
    ico = [s for b in [(0, 1, PHI)] for p in even_perms(b) for s in signed(p)]
    dod = list(signed((1, 1, 1))) + [s for p in even_perms((0, PHI, 1 / PHI)) for s in signed(p)]
    faces = []
    for n, k in [(n, 5) for n in ico] + [(n, 6) for n in dod]:
        n = norm(n); ds = sorted(verts, key=lambda v: -dot(v, n))
        f = ds[:k]; c = mul(tuple(map(sum, zip(*f))), 1 / k)
        u = norm(sub(f[0], c)); w = cross(n, u)
        f.sort(key=lambda v: math.atan2(dot(sub(v, c), w), dot(sub(v, c), u)))
        faces.append((k, n, c, f))
    assert len(faces) == 32
    return faces


def rot_to_z(n):
    """Rotation matrix taking unit vector n to +z."""
    z = (0, 0, 1); v = cross(n, z); s = math.sqrt(dot(v, v)); c = dot(n, z)
    if s < 1e-9: return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    vx = [[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]
    vx2 = [[sum(vx[i][k] * vx[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    f = (1 - c) / (s * s)
    return [[(i == j) + vx[i][j] + vx2[i][j] * f for j in range(3)] for i in range(3)]


def rotz(deg):
    a = math.radians(deg); return [[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]]
def rotx(deg):
    a = math.radians(deg); return [[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]]
def matmul(A, B): return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def apply(M, v): return tuple(sum(M[i][k] * v[k] for k in range(3)) for i in range(3))


def hankin(face, theta):
    """Star polygon (alternating midpoints and inner points) for a regular face, in 3D."""
    k, n, c, f = face
    mids = [mul(add(f[i], f[(i + 1) % k]), 0.5) for i in range(k)]
    # inner point X_i lies on the ray c→f[i+1]; distance found in the face's own 2D frame
    apo = math.sqrt(dot(sub(mids[0], c), sub(mids[0], c)))
    half = math.sqrt(dot(sub(f[1], mids[0]), sub(f[1], mids[0])))
    R = math.sqrt(apo * apo + half * half)
    # local frame: centre at origin, midpoint M=(0,-apo), vertex V=(half,-apo). Ray from M at angle θ off the
    # edge (towards V, turned inward) meets the centre→V line at distance rr from the centre.
    t = math.radians(theta)
    sdist = apo / (math.sin(t) + apo * math.cos(t) / half)
    rr = sdist * math.cos(t) * R / half
    xs = [add(c, mul(norm(sub(f[(i + 1) % k], c)), rr)) for i in range(k)]
    star = []
    for i in range(k):
        star += [mids[i], xs[i]]
    return star


def ball(cx, cy, radius, theta=62, tilt=0, spin=0):
    """Projected faces + Hankin stars. Returns list of (kind, depth, face2d, star2d, centre2d, normal_z)."""
    faces = truncated_icosahedron()
    top = norm((0, 1, PHI))
    M = matmul(rotx(tilt), matmul(rotz(spin), rot_to_z(top)))
    Rmax = max(math.sqrt(dot(v, v)) for v in faces[0][3])
    s = radius / Rmax
    P = lambda v: (cx + s * apply(M, v)[0], cy - s * apply(M, v)[1])
    out = []
    for face in faces:
        k, n, c, f = face
        nz = apply(M, n)[2]
        if nz <= 0.02: continue
        star = hankin(face, theta)
        out.append((k, apply(M, c)[2], [P(v) for v in f], [P(v) for v in star], P(c), nz))
    out.sort(key=lambda o: o[1])
    return out
