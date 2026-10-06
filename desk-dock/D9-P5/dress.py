"""Printable cosmetic edge treatment for D9 parts, with protected mating zones.

Rules (same as the R4 bracket):
- Edges parallel to the part's print-Z axis print as perimeters, so they take
  fillets freely: concave corners get `inside` radius, convex ones `outside`.
- Edges on the top face take a 45-degree chamfer (OCC chamfer on straight
  edges; skipped where it fails). Bottom (bed) edges are never touched.
- Any edge whose centre lies within `tol` of a protected solid is skipped:
  pin bores, key slots, sockets, T joints, seam faces, the air cavity, fan
  seats, guard bars, the laptop contact band.
Every operation is validated (single valid solid) and reported; a failed
fillet is retried at half radius, then skipped, never forced.
"""
import cadquery as cq


def _perp(axis):
    a = cq.Vector(*axis).normalized()
    helper = cq.Vector(0, 0, 1) if abs(a.z) < 0.9 else cq.Vector(1, 0, 0)
    u = a.cross(helper).normalized()
    v = a.cross(u).normalized()
    return a, u, v


def _protected(edge, protect, tol):
    center = edge.Center()
    vertex = cq.Vertex.makeVertex(*center.toTuple())
    for solid in protect:
        try:
            # Inside counts as protected: distance() measures to the boundary,
            # so a tab corner deep in the air cavity would otherwise look far away.
            if solid.isInside(center) or solid.distance(vertex) <= tol:
                return True
        except Exception:
            return True
    return False


def axis_edges(shape, axis, min_len):
    a, _, _ = _perp(axis)
    out = []
    for e in shape.Edges():
        if e.geomType() != 'LINE' or e.Length() < min_len:
            continue
        d = (e.endPoint() - e.startPoint()).normalized()
        if abs(d.dot(a)) > 0.999:
            out.append(e)
    return out


def classify(shape, edge, axis):
    _, u, v = _perp(axis)
    c = edge.Center()
    return sum(shape.isInside(c + u * (0.4 * su) + v * (0.4 * sv)) for su in (1, -1) for sv in (1, -1))


def _find(shape, axis, y, z, key):
    return [e for e in axis_edges(shape, axis, 1.0) if (e.Center() - key).Length < 0.02]


def fillet_profile(shape, axis, protect, inside, outside, min_len=3.0, tol=0.6):
    report = {'inside': 0, 'outside': 0, 'protected': 0, 'skipped': []}
    plan = []
    for e in axis_edges(shape, axis, min_len):
        if _protected(e, protect, tol):
            report['protected'] += 1
            continue
        n = classify(shape, e, axis)
        if n == 3:
            plan.append((e.Center(), inside, 'inside'))
        elif n == 1:
            plan.append((e.Center(), outside, 'outside'))
    for kind, radius in (('inside', inside), ('outside', outside)):
        centers = [c for c, r, k in plan if k == kind]
        if not centers:
            continue
        # Batch first; fall back to one edge at a time with a half-radius retry.
        edges = [e for e in axis_edges(shape, axis, 1.0) if any((e.Center() - c).Length < 0.02 for c in centers)]
        try:
            trial = shape.fillet(radius, edges)
            assert trial.isValid() and len(trial.Solids()) == 1
            shape = trial; report[kind] += len(edges); continue
        except Exception:
            pass
        for c in centers:
            done = False
            for r in (radius, radius / 2):
                match = [e for e in axis_edges(shape, axis, 1.0) if (e.Center() - c).Length < 0.02]
                if len(match) != 1:
                    break
                try:
                    trial = shape.fillet(r, match)
                    assert trial.isValid() and len(trial.Solids()) == 1
                    shape = trial; report[kind] += 1; done = True; break
                except Exception as error:
                    last = type(error).__name__
            if not done:
                report['skipped'].append([kind, [round(v, 1) for v in c.toTuple()]])
    return shape, report


def chamfer_top(shape, axis, protect, size, min_len=20.0, tol=0.6):
    """Chamfer straight top-face edges (face normal = +axis) that are long and unprotected."""
    a, _, _ = _perp(axis)
    report = {'chamfered': 0, 'skipped': []}
    top_faces = [f for f in shape.Faces() if f.geomType() == 'PLANE' and f.normalAt().dot(a) > 0.999]
    if not top_faces:
        return shape, report
    zmax = max(f.Center().dot(a) for f in top_faces)
    top_faces = [f for f in top_faces if abs(f.Center().dot(a) - zmax) < 1e-3]
    candidates = []
    for f in top_faces:
        for e in f.Edges():
            if e.geomType() == 'LINE' and e.Length() >= min_len and not _protected(e, protect, tol):
                candidates.append(e.Center())
    for c in candidates:
        match = [e for e in shape.Edges() if e.geomType() == 'LINE' and (e.Center() - c).Length < 0.02]
        if len(match) != 1:
            continue
        try:
            trial = shape.chamfer(size, None, match)
            assert trial.isValid() and len(trial.Solids()) == 1
            shape = trial; report['chamfered'] += 1
        except Exception as error:
            report['skipped'].append([[round(v, 1) for v in c.toTuple()], type(error).__name__])
    return shape, report


def dress(shape, axis, protect, inside=3.0, outside=1.5, top_chamfer=0.0):
    shape, fr = fillet_profile(shape, axis, protect, inside, outside)
    cr = {'chamfered': 0, 'skipped': []}
    if top_chamfer:
        shape, cr = chamfer_top(shape, axis, protect, top_chamfer)
    shape = shape.clean()
    assert shape.isValid() and len(shape.Solids()) == 1
    return shape, {'fillets': fr, 'top_chamfer': cr}
