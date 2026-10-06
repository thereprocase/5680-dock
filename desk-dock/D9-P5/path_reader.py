"""Parse actual Orca extrusion roads with exact circular-arc extrema."""
import math,re

def paths(text):
    pos = dict(X=0., Y=0., Z=0., E=0.)
    relative_e, absolute_xyz, role = True, True, 'Custom'
    segments = []
    for line in text.splitlines():
        if line.startswith('; FEATURE: '):
            role = line[11:]
            continue
        code = line.split(';')[0].strip()
        if not code:
            continue
        op = code.split()[0]
        if op == 'M83': relative_e = True
        if op == 'M82': relative_e = False
        if op == 'G90': absolute_xyz = True
        if op == 'G91': absolute_xyz = False
        values = {k:float(v) for k,v in re.findall(r'([XYZEIJ])([-+]?(?:\d*\.)?\d+)', code)}
        if op == 'G92':
            pos.update({k:v for k,v in values.items() if k in pos})
            continue
        if op not in ('G0','G1','G2','G3'):
            continue
        before = pos.copy()
        for k in ('X','Y','Z'):
            if k in values:
                pos[k] = values[k] if absolute_xyz else pos[k]+values[k]
        extrusion = values.get('E',0) if relative_e else values.get('E',pos['E'])-pos['E']
        if 'E' in values:
            pos['E'] = pos['E']+values['E'] if relative_e else values['E']
        if extrusion <= 0 or role == 'Custom':
            continue
        p0, p1 = (before['X'],before['Y']), (pos['X'],pos['Y'])
        if p0 == p1 and op not in ('G2','G3'):
            continue
        arc = [p0,p1]
        if op in ('G2','G3'):
            assert 'I' in values or 'J' in values, 'Unsupported arc encoding'
            cx,cy = p0[0]+values.get('I',0),p0[1]+values.get('J',0)
            a,b = math.atan2(p0[1]-cy,p0[0]-cx),math.atan2(p1[1]-cy,p1[0]-cx)
            sweep = (b-a)%(2*math.pi) if op == 'G3' else -((a-b)%(2*math.pi))
            if abs(sweep) < 1e-9: sweep = 2*math.pi*(1 if op == 'G3' else -1)
            count = max(2,math.ceil(abs(sweep)/.5))
            radius = math.hypot(p0[0]-cx,p0[1]-cy)
            fractions=[i/count for i in range(count+1)]
            # Exact cardinal extrema preserve boundary checks without making
            # hundreds of preview chords for every short circular road.
            for cardinal in (0,math.pi/2,math.pi,3*math.pi/2):
                delta=(cardinal-a)%(2*math.pi) if sweep>0 else -((a-cardinal)%(2*math.pi))
                fraction=delta/sweep
                if 0<fraction<1:fractions.append(fraction)
            arc = [(cx+radius*math.cos(a+sweep*f),cy+radius*math.sin(a+sweep*f)) for f in sorted(fractions)]
        segments.extend((a,b,pos['Z'],role) for a,b in zip(arc,arc[1:]))
    return segments

