from flask import Flask, request, jsonify
import sqlite3, base64, os, json, random, uuid
from datetime import datetime

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jloset.db')

# ── DATABASE ──────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS garments (
            id TEXT PRIMARY KEY, filename TEXT, image_data TEXT,
            category TEXT, uploaded_at TEXT
        );
        CREATE TABLE IF NOT EXISTS outfits (
            id TEXT PRIMARY KEY, garment_id TEXT, title TEXT, description TEXT,
            occasion TEXT, season TEXT, style_vibe TEXT,
            items_suggestion TEXT, color_palette TEXT, created_at TEXT,
            FOREIGN KEY (garment_id) REFERENCES garments(id)
        );
        CREATE TABLE IF NOT EXISTS saves (
            id TEXT PRIMARY KEY, outfit_id TEXT, saved_at TEXT,
            FOREIGN KEY (outfit_id) REFERENCES outfits(id)
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# ── STYLE ENGINE ──────────────────────────────────────────────────────────────

PALETTE = {
    "casual":  ["#e8ddd0","#c9b99a","#a08060","#7a5c3e","#f2ece4"],
    "formal":  ["#d6cfc4","#b09880","#8a7060","#5a4030","#f0ebe3"],
    "trendy":  ["#e0d4c0","#c4a878","#a07840","#7a5020","#f5ede0"],
    "boho":    ["#ddd0b8","#c0a060","#906830","#604010","#f0e8d4"],
    "minimal": ["#ede8e0","#ccc0b0","#a09080","#706050","#f8f4ee"],
    "edgy":    ["#d0c8bc","#b09080","#806858","#504030","#eee8e0"],
}

OUTFIT_DATA = [
    {
        "title": "Golden Hour",
        "description": "Sun-warmed tones and effortless layers. The kind of look that catches every bit of light in the room.",
        "style_vibe": "casual", "occasion": "Brunch", "season": "All Season",
        "pair_with": "wide-leg linen trousers",
        "accessories": ["gold hoop earrings", "woven tote", "strappy sandals"],
        "img": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=700&q=85"
    },
    {
        "title": "Quiet Luxury",
        "description": "Understated and precise. Clean silhouettes, premium textures, and the confidence of not needing to try.",
        "style_vibe": "formal", "occasion": "Office", "season": "Fall/Winter",
        "pair_with": "tailored wide-leg trousers",
        "accessories": ["structured leather bag", "minimal gold watch", "pointed-toe loafers"],
        "img": "https://images.unsplash.com/photo-1548142813-c348350df52b?w=700&q=85"
    },
    {
        "title": "Pinterest Mood",
        "description": "The look that gets saved a thousand times. Every detail considered, nothing accidental.",
        "style_vibe": "trendy", "occasion": "Content Day", "season": "Spring/Summer",
        "pair_with": "barrel-leg jeans",
        "accessories": ["micro bag", "layered gold chains", "square-toe mules"],
        "img": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=700&q=85"
    },
    {
        "title": "Desert Rose",
        "description": "Earthy warmth meets effortless movement. Flowing fabrics in dusty, sun-bleached tones.",
        "style_vibe": "boho", "occasion": "Weekend", "season": "Summer",
        "pair_with": "flowy midi skirt",
        "accessories": ["turquoise rings", "leather belt", "flat sandals"],
        "img": "https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=700&q=85"
    },
    {
        "title": "Clean Canvas",
        "description": "Everything stripped back to its essence. Neutral architecture for the modern wardrobe.",
        "style_vibe": "minimal", "occasion": "Gallery", "season": "All Season",
        "pair_with": "straight-leg cream trousers",
        "accessories": ["sculptural earrings", "minimalist tote", "white sneakers"],
        "img": "https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=700&q=85"
    },
    {
        "title": "After Dark",
        "description": "The outfit that shifts seamlessly once the sun goes down. Bold where it counts.",
        "style_vibe": "edgy", "occasion": "Night Out", "season": "All Season",
        "pair_with": "leather straight-leg pants",
        "accessories": ["statement earrings", "thigh-high boots", "micro clutch"],
        "img": "https://images.unsplash.com/photo-1509631179647-0177331693ae?w=700&q=85"
    },
    {
        "title": "Linen & Light",
        "description": "Breathable ease for warm days. Relaxed fits and natural fibres that look better slightly rumpled.",
        "style_vibe": "casual", "occasion": "Market Day", "season": "Summer",
        "pair_with": "linen wide-leg shorts",
        "accessories": ["raffia bag", "white sneakers", "pearl stud earrings"],
        "img": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=700&q=85"
    },
    {
        "title": "Power Hour",
        "description": "Dressed for the room you want to walk into. Sharp lines, deliberate choices.",
        "style_vibe": "formal", "occasion": "Business Meeting", "season": "Fall",
        "pair_with": "slim cigarette trousers",
        "accessories": ["silk scarf", "leather portfolio", "block-heel pumps"],
        "img": "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=700&q=85"
    },
    {
        "title": "Caramel Dream",
        "description": "Warm honey tones layered with intention. The palette of late afternoons and good memories.",
        "style_vibe": "trendy", "occasion": "Dinner Date", "season": "Fall",
        "pair_with": "chocolate midi skirt",
        "accessories": ["gold cuff bracelet", "kitten heel mules", "lip-gloss clutch"],
        "img": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=700&q=85"
    },
    {
        "title": "Studio Session",
        "description": "Creative ease with an edge. The outfit of someone who makes things.",
        "style_vibe": "edgy", "occasion": "Creative Work", "season": "All Season",
        "pair_with": "vintage wash denim",
        "accessories": ["silver rings stack", "canvas tote", "chunky boots"],
        "img": "https://images.unsplash.com/photo-1485462537746-965f33f7f6a7?w=700&q=85"
    },
    {
        "title": "Soft Morning",
        "description": "Gentle neutrals and cozy silhouettes. Comfort elevated to an art form.",
        "style_vibe": "minimal", "occasion": "Coffee Run", "season": "Spring",
        "pair_with": "oversized knit cardigan",
        "accessories": ["claw clip", "crossbody bag", "white low-top sneakers"],
        "img": "https://images.unsplash.com/photo-1502716119720-b23a93e5fe1b?w=700&q=85"
    },
    {
        "title": "Terracotta Sky",
        "description": "The richness of earth tones in a silhouette that moves. Organic and striking.",
        "style_vibe": "boho", "occasion": "Outdoor Event", "season": "Spring/Summer",
        "pair_with": "wide-leg terracotta trousers",
        "accessories": ["beaded necklace", "leather sandals", "woven bucket hat"],
        "img": "https://images.unsplash.com/photo-1566206091558-7f218b696731?w=700&q=85"
    },
]

def detect_category(filename):
    n = filename.lower()
    if any(w in n for w in ['shirt','top','blouse','tee','sweater','knit','crop','tank']): return 'top'
    if any(w in n for w in ['pant','trouser','jean','skirt','short','bottom','legging']): return 'bottom'
    if any(w in n for w in ['dress','gown','maxi','midi','jumpsuit']): return 'dress'
    if any(w in n for w in ['jacket','coat','blazer','cardigan','hoodie','outer','vest']): return 'jacket'
    if any(w in n for w in ['shoe','boot','heel','sneaker','sandal','loafer','flat']): return 'shoes'
    if any(w in n for w in ['bag','purse','clutch','tote']): return 'bag'
    return random.choice(['top','bottom','dress','jacket'])

def generate_outfits(garment_id):
    picks = random.sample(OUTFIT_DATA, min(9, len(OUTFIT_DATA)))
    outfits = []
    for o in picks:
        palette = PALETTE.get(o['style_vibe'], PALETTE['casual'])
        outfit = {
            'id': str(uuid.uuid4()),
            'garment_id': garment_id,
            'title': o['title'],
            'description': o['description'],
            'occasion': o['occasion'],
            'season': o['season'],
            'style_vibe': o['style_vibe'],
            'items_suggestion': json.dumps({
                'image_url': o['img'],
                'pair_with': o['pair_with'],
                'accessories': o['accessories']
            }),
            'color_palette': json.dumps(palette),
            'created_at': datetime.utcnow().isoformat()
        }
        outfits.append(outfit)
    return outfits

# ── API ROUTES ────────────────────────────────────────────────────────────────

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    f = request.files['image']
    data = f.read()
    b64 = base64.b64encode(data).decode()
    ext = f.filename.rsplit('.',1)[-1].lower() if '.' in f.filename else 'jpg'
    mime = f"image/{ext}" if ext in ['jpg','jpeg','png','webp','gif'] else 'image/jpeg'
    img_url = f"data:{mime};base64,{b64}"
    gid = str(uuid.uuid4())
    cat = detect_category(f.filename)
    conn = get_db()
    conn.execute('INSERT INTO garments VALUES (?,?,?,?,?)',
                 (gid, f.filename, img_url, cat, datetime.utcnow().isoformat()))
    outfits = generate_outfits(gid)
    for o in outfits:
        conn.execute('INSERT INTO outfits VALUES (?,?,?,?,?,?,?,?,?,?)',
                     (o['id'],o['garment_id'],o['title'],o['description'],
                      o['occasion'],o['season'],o['style_vibe'],
                      o['items_suggestion'],o['color_palette'],o['created_at']))
    conn.commit(); conn.close()
    result = []
    for o in outfits:
        d = dict(o)
        d['items_suggestion'] = json.loads(d['items_suggestion'])
        d['color_palette'] = json.loads(d['color_palette'])
        result.append(d)
    return jsonify({'garment_id': gid, 'category': cat, 'image': img_url, 'outfits': result})

@app.route('/api/save', methods=['POST'])
def save():
    oid = request.json.get('outfit_id')
    conn = get_db()
    ex = conn.execute('SELECT id FROM saves WHERE outfit_id=?',(oid,)).fetchone()
    if ex:
        conn.execute('DELETE FROM saves WHERE outfit_id=?',(oid,))
        conn.commit(); conn.close()
        return jsonify({'saved': False})
    conn.execute('INSERT INTO saves VALUES (?,?,?)',
                 (str(uuid.uuid4()), oid, datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    return jsonify({'saved': True})

@app.route('/api/saved')
def get_saved():
    conn = get_db()
    rows = conn.execute('''
        SELECT o.*, g.image_data as garment_image, g.category as garment_cat
        FROM saves s JOIN outfits o ON s.outfit_id=o.id
        JOIN garments g ON o.garment_id=g.id ORDER BY s.saved_at DESC
    ''').fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        d['items_suggestion'] = json.loads(d['items_suggestion'])
        d['color_palette'] = json.loads(d['color_palette'])
        result.append(d)
    return jsonify(result)

@app.route('/api/saved_ids')
def saved_ids():
    conn = get_db()
    rows = conn.execute('SELECT outfit_id FROM saves').fetchall()
    conn.close()
    return jsonify([r['outfit_id'] for r in rows])

# ── FRONTEND (EMBEDDED) ───────────────────────────────────────────────────────

HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Jloset</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&family=Jost:wght@200;300;400;500&display=swap" rel="stylesheet"/>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{
  --c:#faf6f0;--w:#fdf9f4;--b:#ede7dc;--t:#d4c5ae;--m:#9e8470;
  --ca:#c4a472;--e:#4a3828;--dk:#251a10;--ro:#e8d2c0;--sh:rgba(74,56,40,.09);
  --shd:rgba(74,56,40,.16);
}
html{scroll-behavior:smooth}
body{background:var(--c);color:var(--dk);font-family:'Jost',sans-serif;font-weight:300;overflow-x:hidden}
body::after{content:'';position:fixed;inset:0;background:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23n)' opacity='.035'/%3E%3C/svg%3E");pointer-events:none;z-index:9999;opacity:.5}

/* NAV */
nav{position:fixed;top:0;left:0;right:0;z-index:200;display:flex;align-items:center;justify-content:space-between;padding:18px 56px;background:rgba(250,246,240,.88);backdrop-filter:blur(24px);border-bottom:1px solid var(--b)}
.logo{font-family:'Cormorant Garamond',serif;font-size:26px;font-weight:300;letter-spacing:.1em;color:var(--e);cursor:pointer;user-select:none}
.logo em{font-style:italic;color:var(--ca)}
.nav-links{display:flex;gap:40px;list-style:none}
.nav-links a{font-size:11px;font-weight:400;letter-spacing:.18em;text-transform:uppercase;color:var(--m);text-decoration:none;transition:color .2s;cursor:pointer}
.nav-links a:hover,.nav-links a.on{color:var(--e)}

/* PAGE TRANSITIONS */
.page{display:none;padding-top:80px}
.page.on{display:block}

/* HERO */
.hero{display:grid;grid-template-columns:1fr 1fr;min-height:calc(100vh - 80px)}
.hero-l{display:flex;flex-direction:column;justify-content:center;padding:80px 56px 80px 80px}
.eyebrow{font-size:10px;letter-spacing:.3em;text-transform:uppercase;color:var(--ca);margin-bottom:28px;display:flex;align-items:center;gap:14px}
.eyebrow::before{content:'';width:36px;height:1px;background:var(--ca)}
.h1{font-family:'Cormorant Garamond',serif;font-size:clamp(54px,6.5vw,96px);font-weight:300;line-height:1.03;color:var(--dk);margin-bottom:28px}
.h1 em{font-style:italic;color:var(--ca)}
.hero-sub{font-size:15px;font-weight:300;color:var(--m);line-height:1.75;max-width:400px;margin-bottom:52px}
.hero-r{position:relative;overflow:hidden;background:var(--b)}
.collage{position:absolute;inset:0;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:2px}
.collage-cell{overflow:hidden}
.collage-cell img{width:100%;height:100%;object-fit:cover;transition:transform .7s ease}
.collage-cell:hover img{transform:scale(1.05)}
.hero-r::after{content:'';position:absolute;inset:0;background:linear-gradient(135deg,rgba(250,246,240,.12) 0,transparent 55%);pointer-events:none}
.hero-pill{position:absolute;bottom:36px;left:36px;background:var(--c);border-radius:14px;padding:14px 20px;font-size:12px;box-shadow:0 8px 28px var(--shd);z-index:10;border:1px solid var(--b)}
.hero-pill strong{font-family:'Cormorant Garamond',serif;font-size:26px;display:block;color:var(--e);line-height:1}

/* UPLOAD */
.drop-zone{border:1.5px dashed var(--t);border-radius:20px;padding:36px 32px;text-align:center;cursor:pointer;transition:all .3s;background:var(--w);position:relative;overflow:hidden;max-width:400px}
.drop-zone::before{content:'';position:absolute;inset:0;background:radial-gradient(circle,rgba(196,164,114,.07),transparent 70%);opacity:0;transition:opacity .3s}
.drop-zone:hover::before,.drop-zone.over::before{opacity:1}
.drop-zone:hover,.drop-zone.over{border-color:var(--ca);transform:translateY(-3px);box-shadow:0 18px 52px var(--shd)}
.drop-icon{width:52px;height:52px;background:var(--b);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 18px;font-size:20px}
.drop-main{font-family:'Cormorant Garamond',serif;font-size:19px;color:var(--e);margin-bottom:6px}
.drop-sub{font-size:12px;color:var(--m);margin-bottom:20px}
.btn-upload{background:var(--e);color:var(--c);border:none;padding:13px 30px;border-radius:100px;font-family:'Jost',sans-serif;font-size:12px;font-weight:400;letter-spacing:.1em;cursor:pointer;transition:all .2s}
.btn-upload:hover{background:var(--dk);transform:translateY(-1px);box-shadow:0 8px 24px var(--shd)}
#fi{display:none}

/* SECTION COMMON */
section{padding:100px 80px}
.s-label{font-size:10px;letter-spacing:.28em;text-transform:uppercase;color:var(--ca);margin-bottom:14px;display:flex;align-items:center;gap:12px}
.s-label::before{content:'';width:24px;height:1px;background:var(--ca)}
.s-title{font-family:'Cormorant Garamond',serif;font-size:clamp(38px,4.5vw,60px);font-weight:300;color:var(--dk);line-height:1.1;margin-bottom:14px}
.s-sub{font-size:14px;color:var(--m);line-height:1.75;max-width:460px;margin-bottom:52px}

/* RESULTS */
#results{display:none;background:var(--w)}
.res-head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:44px;flex-wrap:wrap;gap:20px}
.garment-chip{display:flex;align-items:center;gap:16px;background:var(--c);border:1px solid var(--b);border-radius:16px;padding:12px 20px}
.g-thumb{width:56px;height:70px;border-radius:10px;object-fit:cover;border:1px solid var(--t)}
.g-label{font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:var(--m);margin-bottom:3px}
.g-cat{font-family:'Cormorant Garamond',serif;font-size:18px;color:var(--e)}
.chips{display:flex;gap:8px;flex-wrap:wrap}
.chip{padding:8px 20px;border-radius:100px;border:1px solid var(--t);background:transparent;font-family:'Jost',sans-serif;font-size:11px;letter-spacing:.08em;color:var(--m);cursor:pointer;transition:all .2s}
.chip:hover,.chip.on{background:var(--e);border-color:var(--e);color:var(--c)}

/* MASONRY */
.masonry{columns:3;column-gap:18px}
@media(max-width:1100px){.masonry{columns:2}}
@media(max-width:640px){.masonry{columns:1}}

.card{break-inside:avoid;margin-bottom:18px;border-radius:18px;overflow:hidden;background:var(--c);border:1px solid var(--b);cursor:pointer;transition:all .35s cubic-bezier(.34,1.56,.64,1);position:relative;animation:ci .5s ease backwards}
@keyframes ci{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}
.card:hover{transform:translateY(-7px) scale(1.01);box-shadow:0 28px 72px var(--shd);border-color:var(--t)}
.card-img{position:relative;overflow:hidden}
.card-img img{width:100%;display:block;transition:transform .55s ease}
.card:hover .card-img img{transform:scale(1.05)}
.card-ov{position:absolute;inset:0;background:linear-gradient(to bottom,transparent 35%,rgba(37,26,16,.6) 100%);opacity:0;transition:opacity .3s;display:flex;flex-direction:column;justify-content:flex-end;padding:18px}
.card:hover .card-ov{opacity:1}
.ov-btns{display:flex;gap:8px}
.ob{flex:1;padding:10px;border-radius:10px;border:none;font-family:'Jost',sans-serif;font-size:11px;font-weight:400;cursor:pointer;transition:all .2s;letter-spacing:.06em}
.ob.p{background:var(--c);color:var(--e)}
.ob.s{flex:0 0 42px;background:rgba(250,246,240,.18);color:var(--c);border:1px solid rgba(250,246,240,.35);backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;font-size:15px}
.ob.s.saved{background:var(--ca);border-color:var(--ca)}
.card-body{padding:18px}
.cv{font-size:9px;letter-spacing:.2em;text-transform:uppercase;color:var(--ca);margin-bottom:8px;display:flex;align-items:center;gap:5px}
.cv::before{content:'';width:4px;height:4px;border-radius:50%;background:var(--ca)}
.ct{font-family:'Cormorant Garamond',serif;font-size:21px;color:var(--e);margin-bottom:7px;line-height:1.2}
.cd{font-size:12px;color:var(--m);line-height:1.65;margin-bottom:14px}
.ctags{display:flex;gap:5px;flex-wrap:wrap;margin-bottom:13px}
.ctag{padding:3px 11px;border-radius:100px;background:var(--b);font-size:10px;color:var(--m)}
.cpair{background:var(--b);border-radius:10px;padding:12px 14px;margin-bottom:11px}
.cpair-l{font-size:9px;letter-spacing:.18em;text-transform:uppercase;color:var(--ca);margin-bottom:3px}
.cpair-v{font-size:13px;color:var(--e);text-transform:capitalize}
.cpal{display:flex;gap:5px;align-items:center;margin-bottom:10px}
.pd{width:16px;height:16px;border-radius:50%;border:1.5px solid rgba(255,255,255,.55);box-shadow:0 1px 4px var(--sh)}
.cacc{font-size:11px;color:var(--m);line-height:1.6}
.cacc b{color:var(--e);font-weight:500}

/* HOW */
.how{background:var(--b);position:relative;overflow:hidden}
.how::before{content:'Jloset';position:absolute;font-family:'Cormorant Garamond',serif;font-size:300px;font-weight:300;color:rgba(212,197,174,.35);right:-20px;bottom:-60px;line-height:1;pointer-events:none;letter-spacing:-.02em}
.how-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;position:relative;z-index:1}
@media(max-width:800px){.how-grid{grid-template-columns:1fr}}
.hc{background:var(--c);border-radius:18px;padding:32px 28px;border:1px solid var(--t);transition:all .3s}
.hc:hover{transform:translateY(-5px);box-shadow:0 18px 48px var(--shd)}
.hn{font-family:'Cormorant Garamond',serif;font-size:68px;font-weight:300;color:var(--b);line-height:1;margin-bottom:18px}
.ht{font-family:'Cormorant Garamond',serif;font-size:22px;color:var(--e);margin-bottom:10px}
.htext{font-size:13px;color:var(--m);line-height:1.7}

/* LOADING */
#loading{display:none;position:fixed;inset:0;background:rgba(250,246,240,.92);backdrop-filter:blur(12px);z-index:400;flex-direction:column;align-items:center;justify-content:center;gap:22px}
#loading.on{display:flex}
.spin{width:44px;height:44px;border:2px solid var(--b);border-top-color:var(--ca);border-radius:50%;animation:sp .75s linear infinite}
@keyframes sp{to{transform:rotate(360deg)}}
.lt{font-family:'Cormorant Garamond',serif;font-size:22px;color:var(--e);font-style:italic}
.ls{font-size:12px;color:var(--m);letter-spacing:.1em}

/* MODAL */
#mbg{display:none;position:fixed;inset:0;background:rgba(37,26,16,.52);backdrop-filter:blur(10px);z-index:300;align-items:center;justify-content:center;padding:20px}
#mbg.on{display:flex}
.modal{background:var(--c);border-radius:24px;max-width:700px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 40px 100px rgba(37,26,16,.22);animation:mi .35s cubic-bezier(.34,1.56,.64,1);scrollbar-width:thin;scrollbar-color:var(--t) transparent;position:relative}
@keyframes mi{from{opacity:0;transform:scale(.9) translateY(24px)}to{opacity:1;transform:scale(1) translateY(0)}}
.mi{width:100%;height:300px;object-fit:cover;border-radius:24px 24px 0 0;display:block}
.mb{padding:32px}
.mc{position:absolute;top:16px;right:16px;width:38px;height:38px;border-radius:50%;background:var(--c);border:none;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 16px var(--shd);transition:all .2s}
.mc:hover{transform:scale(1.1)}
.mtt{font-family:'Cormorant Garamond',serif;font-size:34px;font-weight:300;color:var(--e);margin-bottom:10px}
.mtags{display:flex;gap:7px;margin-bottom:18px;flex-wrap:wrap}
.mtag{padding:5px 14px;border-radius:100px;border:1px solid var(--t);font-size:11px;color:var(--m);letter-spacing:.07em}
.mdesc{font-size:14px;color:var(--m);line-height:1.85;margin-bottom:28px;border-left:2px solid var(--ca);padding-left:18px;font-style:italic}
.msl{font-size:10px;letter-spacing:.2em;text-transform:uppercase;color:var(--ca);margin-bottom:12px;margin-top:24px}
.maccs{display:flex;flex-wrap:wrap;gap:7px}
.macc{padding:7px 16px;border-radius:100px;background:var(--b);font-size:12px;color:var(--e);text-transform:capitalize}
.mpal{display:flex;gap:7px;flex-wrap:wrap}
.mpi{display:flex;align-items:center;gap:7px;background:var(--b);border-radius:100px;padding:5px 12px 5px 7px}
.mps{width:20px;height:20px;border-radius:50%;border:1.5px solid rgba(255,255,255,.65);box-shadow:0 1px 4px var(--sh)}
.mpn{font-size:11px;color:var(--e);text-transform:capitalize}
.mctas{margin-top:28px;display:flex;gap:10px}
.btnp{flex:1;padding:15px;background:var(--e);color:var(--c);border:none;border-radius:12px;font-family:'Jost',sans-serif;font-size:13px;letter-spacing:.06em;cursor:pointer;transition:all .2s}
.btnp:hover{background:var(--dk);transform:translateY(-1px);box-shadow:0 8px 24px var(--shd)}
.btns{padding:15px 22px;background:var(--b);color:var(--e);border:none;border-radius:12px;font-family:'Jost',sans-serif;font-size:13px;cursor:pointer;transition:all .2s}
.btns:hover{background:var(--t);color:var(--dk)}

/* SAVED */
#saved-page{background:var(--c)}
.empty{text-align:center;padding:80px 20px}
.ei{font-size:44px;margin-bottom:18px}
.et{font-family:'Cormorant Garamond',serif;font-size:26px;color:var(--e);margin-bottom:8px}
.es{font-size:13px;color:var(--m)}

/* TOAST */
#toast{position:fixed;bottom:28px;left:50%;transform:translateX(-50%) translateY(90px);background:var(--e);color:var(--c);padding:12px 26px;border-radius:100px;font-size:12px;letter-spacing:.07em;z-index:500;transition:transform .35s cubic-bezier(.34,1.56,.64,1);white-space:nowrap}
#toast.on{transform:translateX(-50%) translateY(0)}

/* FOOTER */
footer{background:var(--dk);padding:52px 80px;display:flex;align-items:center;justify-content:space-between}
.fl{font-family:'Cormorant Garamond',serif;font-size:28px;font-weight:300;color:var(--c);letter-spacing:.08em}
.fl em{font-style:italic;color:var(--ca)}
.ft{font-size:12px;color:var(--m);letter-spacing:.08em}

@media(max-width:900px){
  nav{padding:14px 20px}
  .hero{grid-template-columns:1fr}
  .hero-r{height:55vw}
  .hero-l{padding:48px 24px 40px}
  section{padding:60px 24px}
  footer{flex-direction:column;gap:12px;padding:40px 24px;text-align:center}
}
</style>
</head>
<body>

<nav>
  <div class="logo" onclick="go('home')">J<em>loset</em></div>
  <ul class="nav-links">
    <li><a id="n-home" class="on" onclick="go('home')">Discover</a></li>
    <li><a id="n-saved" onclick="go('saved')">Saved</a></li>
    <li><a onclick="goHow()">How it works</a></li>
  </ul>
</nav>

<div id="loading"><div class="spin"></div><div class="lt">Curating your looks…</div><div class="ls">matching palettes & styling</div></div>
<div id="toast"></div>

<!-- MODAL -->
<div id="mbg" onclick="closeMbg(event)">
  <div class="modal" id="modal">
    <button class="mc" onclick="closeModal()">✕</button>
    <img class="mi" id="mi" src="" alt=""/>
    <div class="mb">
      <div class="mtags" id="mtags"></div>
      <h2 class="mtt" id="mtt"></h2>
      <p class="mdesc" id="mdesc"></p>
      <div class="msl">Pair With</div>
      <p id="mpair" style="font-size:14px;color:var(--e);text-transform:capitalize;margin-bottom:6px"></p>
      <div class="msl">Accessories</div>
      <div class="maccs" id="maccs"></div>
      <div class="msl">Colour Palette</div>
      <div class="mpal" id="mpal"></div>
      <div class="mctas">
        <button class="btnp" id="msavebtn" onclick="saveFromModal()">♡ Save This Look</button>
        <button class="btns" onclick="closeModal()">Close</button>
      </div>
    </div>
  </div>
</div>

<!-- HOME PAGE -->
<div id="pg-home" class="page on">

  <!-- HERO -->
  <div class="hero">
    <div class="hero-l">
      <div class="eyebrow">AI-Powered Styling</div>
      <h1 class="h1">Your wardrobe,<br><em>infinitely</em><br>styled.</h1>
      <p class="hero-sub">Upload any piece from your closet. Get curated outfit ideas with pairings, palettes, and accessories — instantly.</p>
      <div class="drop-zone" id="dz"
           onclick="document.getElementById('fi').click()"
           ondragover="dov(event)" ondragleave="dlv(event)" ondrop="ddrop(event)">
        <div class="drop-icon">✦</div>
        <div class="drop-main">Drop your garment here</div>
        <div class="drop-sub">PNG · JPG · WEBP — any piece welcome</div>
        <button class="btn-upload" onclick="event.stopPropagation();document.getElementById('fi').click()">Browse files</button>
        <input type="file" id="fi" accept="image/*" onchange="handleFile(event)"/>
      </div>
    </div>
    <div class="hero-r">
      <div class="collage">
        <div class="collage-cell"><img src="https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&q=80" alt=""/></div>
        <div class="collage-cell"><img src="https://images.unsplash.com/photo-1469334031218-e382a71b716b?w=600&q=80" alt=""/></div>
        <div class="collage-cell"><img src="https://images.unsplash.com/photo-1548142813-c348350df52b?w=600&q=80" alt=""/></div>
        <div class="collage-cell"><img src="https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600&q=80" alt=""/></div>
      </div>
      <div class="hero-pill"><strong>9+</strong>outfit ideas per upload</div>
    </div>
  </div>

  <!-- RESULTS -->
  <section id="results">
    <div class="res-head">
      <div>
        <div class="s-label">Style Suggestions</div>
        <h2 class="s-title" id="res-title">Your Looks</h2>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:14px">
        <div class="garment-chip" id="gchip" style="display:none">
          <img class="g-thumb" id="gthumb" src="" alt=""/>
          <div><div class="g-label">Uploaded piece</div><div class="g-cat" id="gcat">—</div></div>
        </div>
        <div class="chips">
          <button class="chip on" onclick="filterBy('all',this)">All</button>
          <button class="chip" onclick="filterBy('casual',this)">Casual</button>
          <button class="chip" onclick="filterBy('formal',this)">Formal</button>
          <button class="chip" onclick="filterBy('trendy',this)">Trendy</button>
          <button class="chip" onclick="filterBy('boho',this)">Boho</button>
          <button class="chip" onclick="filterBy('minimal',this)">Minimal</button>
          <button class="chip" onclick="filterBy('edgy',this)">Edgy</button>
        </div>
      </div>
    </div>
    <div class="masonry" id="grid"></div>
  </section>

  <!-- HOW IT WORKS -->
  <section class="how" id="how">
    <div class="s-label">The Process</div>
    <h2 class="s-title">How Jloset works</h2>
    <p class="s-sub">Three effortless steps to endless outfit inspiration.</p>
    <div class="how-grid">
      <div class="hc"><div class="hn">01</div><div class="ht">Upload any garment</div><div class="htext">Photo or image of any clothing piece — jacket, dress, trousers, shoes, anything from your wardrobe.</div></div>
      <div class="hc"><div class="hn">02</div><div class="ht">Get styled instantly</div><div class="htext">The style engine generates curated combinations with colour palettes, pairings, and accessory suggestions.</div></div>
      <div class="hc"><div class="hn">03</div><div class="ht">Save your favourites</div><div class="htext">Pin the looks you love. Build your personal mood board and revisit your saved inspirations anytime.</div></div>
    </div>
  </section>

</div>

<!-- SAVED PAGE -->
<div id="pg-saved" class="page" style="background:var(--c)">
  <section>
    <div class="s-label">Your Board</div>
    <h2 class="s-title">Saved Looks</h2>
    <p class="s-sub">Your curated collection of outfit inspirations.</p>
    <div class="masonry" id="sgrid"></div>
    <div class="empty" id="sempty" style="display:none"><div class="ei">🤍</div><div class="et">Nothing saved yet</div><div class="es">Upload a garment and save the looks you love.</div></div>
  </section>
</div>

<footer>
  <div class="fl">J<em>loset</em></div>
  <div class="ft">Style your world, one piece at a time.</div>
</footer>

<script>
const COLORS={
  "warm white":"#fdf9f5","sand":"#d4c5aa","camel":"#c4a15a","sage":"#a8b898",
  "dusty rose":"#d4a0a0","washed denim":"#8a9fb4","terracotta":"#c0714a",
  "ivory":"#f5f0e8","chocolate":"#6b4226","slate grey":"#7a8694","cream":"#faf6f1",
  "tan":"#c9a87c","burgundy":"#7c2d3e","ecru":"#f0ebe0","burnt orange":"#c4632a",
  "off-white":"#f8f5ee","mocha":"#8b6355","butter yellow":"#e8d880","caramel":"#c4a472",
  "#e8ddd0":"#e8ddd0","#c9b99a":"#c9b99a","#a08060":"#a08060","#7a5c3e":"#7a5c3e","#f2ece4":"#f2ece4",
  "#d6cfc4":"#d6cfc4","#b09880":"#b09880","#8a7060":"#8a7060","#5a4030":"#5a4030","#f0ebe3":"#f0ebe3",
  "#e0d4c0":"#e0d4c0","#c4a878":"#c4a878","#a07840":"#a07840","#7a5020":"#7a5020","#f5ede0":"#f5ede0",
  "#ddd0b8":"#ddd0b8","#c0a060":"#c0a060","#906830":"#906830","#604010":"#604010","#f0e8d4":"#f0e8d4",
  "#ede8e0":"#ede8e0","#ccc0b0":"#ccc0b0","#a09080":"#a09080","#706050":"#706050","#f8f4ee":"#f8f4ee",
  "#d0c8bc":"#d0c8bc","#b09080":"#b09080","#806858":"#806858","#504030":"#504030","#eee8e0":"#eee8e0"
};
function gc(k){return COLORS[k]||COLORS[k.toLowerCase()]||k}

let all=[],savedSet=new Set(),curModal=null;

// ── NAV ──────────────────────────────────────────────────────────
function go(p){
  document.querySelectorAll('.page').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.nav-links a').forEach(x=>x.classList.remove('on'));
  document.getElementById('pg-'+p).classList.add('on');
  document.getElementById('n-'+p).classList.add('on');
  if(p==='saved')loadSaved();
  window.scrollTo({top:0,behavior:'smooth'});
}
function goHow(){
  go('home');
  setTimeout(()=>document.getElementById('how').scrollIntoView({behavior:'smooth'}),120);
}

// ── DRAG / DROP ──────────────────────────────────────────────────
function dov(e){e.preventDefault();document.getElementById('dz').classList.add('over')}
function dlv(){document.getElementById('dz').classList.remove('over')}
function ddrop(e){e.preventDefault();dlv();const f=e.dataTransfer.files[0];if(f&&f.type.startsWith('image/'))upload(f)}
function handleFile(e){const f=e.target.files[0];if(f)upload(f)}

// ── UPLOAD ───────────────────────────────────────────────────────
async function upload(file){
  document.getElementById('loading').classList.add('on');
  const fd=new FormData();fd.append('image',file);
  try{
    const r=await fetch('/api/upload',{method:'POST',body:fd});
    const d=await r.json();
    if(d.error)throw new Error(d.error);
    all=d.outfits;

    // load saved ids to mark correctly
    const si=await fetch('/api/saved_ids');
    const sids=await si.json();
    savedSet=new Set(sids);

    document.getElementById('gthumb').src=d.image;
    document.getElementById('gcat').textContent=cap(d.category);
    document.getElementById('gchip').style.display='flex';
    document.getElementById('res-title').textContent=`${all.length} Looks for Your ${cap(d.category)}`;
    renderCards(all,'grid');
    document.getElementById('results').style.display='block';
    setTimeout(()=>document.getElementById('results').scrollIntoView({behavior:'smooth'}),100);
    toast('✦ Outfits curated just for you');
  }catch(e){toast('Upload failed. Try again.')}
  finally{document.getElementById('loading').classList.remove('on')}
}

// ── RENDER ───────────────────────────────────────────────────────
function renderCards(outfits,cid){
  const g=document.getElementById(cid);
  g.innerHTML='';
  const hs=['230px','270px','210px','290px','250px','260px','220px','280px','240px'];
  outfits.forEach((o,i)=>{
    const items=typeof o.items_suggestion==='string'?JSON.parse(o.items_suggestion):o.items_suggestion;
    const pal=typeof o.color_palette==='string'?JSON.parse(o.color_palette):o.color_palette;
    const sv=savedSet.has(o.id);
    const ih=hs[i%hs.length];
    const palHtml=pal.slice(0,5).map(c=>`<div class="pd" style="background:${gc(c)}" title="${c}"></div>`).join('');
    const c=document.createElement('div');
    c.className='card';c.style.animationDelay=`${i*.07}s`;c.dataset.vibe=o.style_vibe;c.dataset.id=o.id;
    c.innerHTML=`
      <div class="card-img" style="height:${ih}">
        <img src="${items.image_url}" alt="${o.title}" style="height:${ih};object-fit:cover" loading="lazy"/>
        <div class="card-ov">
          <div class="ov-btns">
            <button class="ob p" onclick="openModal(event,'${o.id}')">View Look</button>
            <button class="ob s${sv?' saved':''}" onclick="doSave(event,'${o.id}',this)">${sv?'♥':'♡'}</button>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div class="cv">${cap(o.style_vibe)}</div>
        <div class="ct">${o.title}</div>
        <div class="cd">${o.description}</div>
        <div class="ctags"><span class="ctag">${o.occasion}</span><span class="ctag">${o.season}</span></div>
        <div class="cpair"><div class="cpair-l">Pair With</div><div class="cpair-v">${items.pair_with}</div></div>
        <div class="cpal">${palHtml}<span style="font-size:10px;color:var(--m);margin-left:3px;letter-spacing:.06em">palette</span></div>
        <div class="cacc"><b>Accessories:</b> ${(items.accessories||[]).join(' · ')}</div>
      </div>`;
    g.appendChild(c);
  });
}

// ── FILTER ───────────────────────────────────────────────────────
function filterBy(v,btn){
  document.querySelectorAll('.chips .chip').forEach(c=>c.classList.remove('on'));
  btn.classList.add('on');
  renderCards(v==='all'?all:all.filter(o=>o.style_vibe===v),'grid');
}

// ── MODAL ────────────────────────────────────────────────────────
function openModal(e,id){
  e.stopPropagation();
  const o=all.find(x=>x.id===id);if(!o)return;
  curModal=o;
  const items=typeof o.items_suggestion==='string'?JSON.parse(o.items_suggestion):o.items_suggestion;
  const pal=typeof o.color_palette==='string'?JSON.parse(o.color_palette):o.color_palette;
  document.getElementById('mi').src=items.image_url;
  document.getElementById('mtt').textContent=o.title;
  document.getElementById('mdesc').textContent=o.description;
  document.getElementById('mpair').textContent=items.pair_with;
  document.getElementById('mtags').innerHTML=
    `<span class="mtag">${cap(o.style_vibe)}</span><span class="mtag">${o.occasion}</span><span class="mtag">${o.season}</span>`;
  document.getElementById('maccs').innerHTML=(items.accessories||[]).map(a=>`<div class="macc">${a}</div>`).join('');
  document.getElementById('mpal').innerHTML=pal.map(c=>
    `<div class="mpi"><div class="mps" style="background:${gc(c)}"></div><span class="mpn">${c}</span></div>`).join('');
  const sv=savedSet.has(o.id);
  const sb=document.getElementById('msavebtn');
  sb.textContent=sv?'♥ Saved':'♡ Save This Look';
  sb.style.background=sv?'var(--ca)':'var(--e)';
  document.getElementById('mbg').classList.add('on');
  document.body.style.overflow='hidden';
}
function closeMbg(e){if(e.target===document.getElementById('mbg'))closeModal()}
function closeModal(){document.getElementById('mbg').classList.remove('on');document.body.style.overflow='';curModal=null}
async function saveFromModal(){if(curModal)await doSaveById(curModal.id)}

// ── SAVE ─────────────────────────────────────────────────────────
async function doSave(e,id,btn){e.stopPropagation();await doSaveById(id,btn)}
async function doSaveById(id,btn){
  const r=await fetch('/api/save',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({outfit_id:id})});
  const d=await r.json();
  if(d.saved){savedSet.add(id);toast('♥ Look saved to your board')}
  else{savedSet.delete(id);toast('Removed from board')}
  // update card button
  const cb=document.querySelector(`[data-id="${id}"] .ob.s`);
  if(cb){cb.textContent=savedSet.has(id)?'♥':'♡';cb.classList.toggle('saved',savedSet.has(id))}
  // update modal btn
  if(curModal&&curModal.id===id){
    const sb=document.getElementById('msavebtn');
    sb.textContent=savedSet.has(id)?'♥ Saved':'♡ Save This Look';
    sb.style.background=savedSet.has(id)?'var(--ca)':'var(--e)';
  }
}

// ── SAVED PAGE ────────────────────────────────────────────────────
async function loadSaved(){
  const r=await fetch('/api/saved');
  const data=await r.json();
  data.forEach(o=>savedSet.add(o.id));
  // merge into all so modal works
  data.forEach(o=>{if(!all.find(x=>x.id===o.id))all.push(o)});
  const g=document.getElementById('sgrid');
  const em=document.getElementById('sempty');
  if(!data.length){g.innerHTML='';em.style.display='block'}
  else{em.style.display='none';renderCards(data,'sgrid')}
}

// ── TOAST ─────────────────────────────────────────────────────────
function toast(msg){
  const t=document.getElementById('toast');
  t.textContent=msg;t.classList.add('on');
  setTimeout(()=>t.classList.remove('on'),2800);
}
function cap(s){return s?s[0].toUpperCase()+s.slice(1):''}
</script>
</body>
</html>"""

@app.route('/')
def index():
    return HTML

if __name__ == '__main__':
    print("\n✦ Jloset is running → http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
