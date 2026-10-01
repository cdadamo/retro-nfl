"""Original retro football touchdown sprites, parameterized for 32 teams."""
load("render.star", "render")
REF = ['...S.................S..', '..SLS...............SLS.', '...LS...............SL..', '...LS...............SL..', '...SSD.............SSL..', '....SL.............SL...', '....SL.............SL...', '....SSD...........SSL...', '.....SL...........SL....', '.....SSD..........SL....', '......SL..WWWWW..SSL....', '......SW.WWWWWWW.SW.....', '......KW.KSSSSK..WK.....', '.......WW.SLSK..WWK.....', '.......KW.SSDK.KWW......', '........WKSSDKWWK.......', '........KWKWKWWK........', '........KWKWKWWK........', '........KWKWKWWW........', '........KWKWKWWK........', '........KWKWKWWK........', '........KWKWKWWK........', '.........WKWKWWK........', '.........WKWKWWK........', '.........WKWKWWK........', '.........KKKKKKK........', '.........KGGGGKK........', '.........KGGGKKK........', '.........KGGKGGK........', '.........KGGKGGK........', '.........KGGKGGK........', '.........KGGKGGK........']
PLAYER = ['......WK................', '.....WWWK...............', '......WWK...............', '......LSK...............', '......LSK...............', '......LSK...............', '......LSK...............', '......LSDK..............', '.......LSK..............', '.......LSK...KKKK.......', '.......SSK..KFFFEK......', '.......SEK..KEEEEEK.....', '.......FEK..KEESSWW.....', '.......HJJKK.KSSDKW.....', '........HJJJJJSSKW......', '........HJJJJJJJK.......', '.........HJJJJJJJK......', '.........JJWWJJJJHK.....', '.........JJJWJJJJHK.....', '.........JJJWJJJKSDK....', '.........JJJWJJJKSLK....', '.........JJWWWJJKLSK....', '.........KJJJJJK.SLK....', '........KJJJJJJKSSK.....', '.......KWWGGWWK.KK......', '......KWWWGGWWK.........', '.....KWWWGKKWWGK........', '.....KWWGK..KWWGK.......', '......KSDK...KWWGK......', '.......KSDK...KWWGK.....', '........KWWK...KSDK.....', '.........KWKK...KSDK....']

def put(c,x,y,color):
    if x>=0 and x<64 and y>=0 and y<32:
        c[y][x]=color

def box(c,x,y,w,h,color):
    for yy in range(y,y+h):
        for xx in range(x,x+w):
            put(c,xx,yy,color)

def line(c,x0,y0,x1,y1,color,width=2):
    steps=max(abs(x1-x0),abs(y1-y0))
    for i in range(steps+1):
        x=x0 if steps==0 else int(x0+(x1-x0)*i/steps)
        y=y0 if steps==0 else int(y0+(y1-y0)*i/steps)
        box(c,x,y,width,width,color)

def sprite(c,pattern,x,y,pal):
    for yy in range(len(pattern)):
        for xx in range(len(pattern[yy])):
            s=pattern[yy][xx]
            if s!='.': put(c,x+xx,y+yy,pal[s])

def background():
    c=[['#101D13' for x in range(64)] for y in range(32)]
    box(c,0,0,64,8,'#9696F4')
    box(c,5,2,8,1,'#FFFFFF')
    box(c,7,1,4,3,'#E9F1FF')
    box(c,35,3,8,1,'#FFFFFF')
    box(c,0,8,64,9,'#181A2B')
    for y in range(9,17):
        for x in range(64):
            if (x*7+y*11)%5<2:
                put(c,x,y,['#A7A397','#55596B','#D0C4A0'][(x+y)%3])
    box(c,0,12,64,1,'#CBD0DD')
    box(c,0,17,64,2,'#959CF0')
    box(c,0,20,64,1,'#E4E4D2')
    box(c,51,0,1,10,'#E9C841')
    box(c,62,0,1,10,'#E9C841')
    box(c,51,9,12,1,'#FFF192')
    box(c,56,10,1,7,'#E9C841')
    return c

def raster(c):
    rows=[]
    for row in c:
        runs=[]
        start=0
        for x in range(1,65):
            if x==64 or row[x]!=row[start]:
                runs.append(render.Box(width=x-start,height=1,color=row[start]))
                start=x
        rows.append(render.Row(children=runs))
    return render.Column(children=rows)

def scene(n,style):
    pal={'K':'#11121B','W':'#FFFFFF','G':'#717E99','S':'#DF9758','L':'#FFE0A1','D':'#975531','J':style['jersey'],'H':style['highlight'],'E':style['helmet'],'F':style['helmet_light']}
    c=background()
    if n<10:
        # A waist-up view gives the arms, neck and tapered shirt enough pixels.
        pose=REF
        if n<3:
            pose=['.'*24 for i in range(10)]+REF[10:]
            line(c,25,17,20,14,pal['S'],2)
            line(c,20,14,18,9,pal['S'],2)
            line(c,36,17,40,14,pal['S'],2)
            line(c,40,14,42,9,pal['S'],2)
        sprite(c,pose,19,0,pal)
    else:
        t=n-10
        # Quarter-turned torso, one raised glove and asymmetrical bent knees.
        # Position changes imply a small hop; the close camera crops the shins.
        lift=[2,1,0,0,0,1,2,2,2,2][t]
        sprite(c,PLAYER,20,lift,pal)
    return raster(c)

STYLES = {'ARI': {'name': 'CARDINALS', 'jersey': '#a40227', 'highlight': '#C1536C', 'helmet': '#FFFFFF', 'helmet_light': '#FFFFFF', 'accent': '#D28093'}, 'ATL': {'name': 'FALCONS', 'jersey': '#a71930', 'highlight': '#C36372', 'helmet': '#171717', 'helmet_light': '#585858', 'accent': '#D38C98'}, 'BAL': {'name': 'RAVENS', 'jersey': '#29126f', 'highlight': '#6D5E9D', 'helmet': '#171717', 'helmet_light': '#585858', 'accent': '#9488B7'}, 'BUF': {'name': 'BILLS', 'jersey': '#00338d', 'highlight': '#5274B1', 'helmet': '#FFFFFF', 'helmet_light': '#FFFFFF', 'accent': '#8099C6'}, 'CAR': {'name': 'PANTHERS', 'jersey': '#0085ca', 'highlight': '#52ACDB', 'helmet': '#BCC4C9', 'helmet_light': '#CFD5D8', 'accent': '#80C2E4'}, 'CHI': {'name': 'BEARS', 'jersey': '#0b1c3a', 'highlight': '#596579', 'helmet': '#0B1C3A', 'helmet_light': '#4F5C71', 'accent': '#858E9C'}, 'CIN': {'name': 'BENGALS', 'jersey': '#fb4f14', 'highlight': '#FC875F', 'helmet': '#FB4F14', 'helmet_light': '#FC8056', 'accent': '#FDA78A'}, 'CLE': {'name': 'BROWNS', 'jersey': '#472a08', 'highlight': '#826E57', 'helmet': '#FF3C00', 'helmet_light': '#FF7347', 'accent': '#A39484'}, 'DAL': {'name': 'COWBOYS', 'jersey': '#002a5c', 'highlight': '#526E90', 'helmet': '#B0B7BC', 'helmet_light': '#C6CBCF', 'accent': '#8094AE'}, 'DEN': {'name': 'BRONCOS', 'jersey': '#0a2343', 'highlight': '#58697F', 'helmet': '#0A2343', 'helmet_light': '#4F6178', 'accent': '#8491A1'}, 'DET': {'name': 'LIONS', 'jersey': '#0076b6', 'highlight': '#52A2CD', 'helmet': '#BBBBBB', 'helmet_light': '#CECECE', 'accent': '#80BADA'}, 'GB': {'name': 'PACKERS', 'jersey': '#204e32', 'highlight': '#678774', 'helmet': '#FFB612', 'helmet_light': '#FFCA54', 'accent': '#90A698'}, 'HOU': {'name': 'TEXANS', 'jersey': '#021018', 'highlight': '#535C62', 'helmet': '#021018', 'helmet_light': '#495359', 'accent': '#80888C'}, 'IND': {'name': 'COLTS', 'jersey': '#003b75', 'highlight': '#527AA1', 'helmet': '#FFFFFF', 'helmet_light': '#FFFFFF', 'accent': '#809DBA'}, 'JAX': {'name': 'JAGUARS', 'jersey': '#007487', 'highlight': '#52A0AD', 'helmet': '#171717', 'helmet_light': '#585858', 'accent': '#80BAC3'}, 'KC': {'name': 'CHIEFS', 'jersey': '#e31837', 'highlight': '#EC6277', 'helmet': '#E31837', 'helmet_light': '#EB596F', 'accent': '#F18C9B'}, 'LV': {'name': 'RAIDERS', 'jersey': '#24242C', 'highlight': '#525252', 'helmet': '#A5ACAF', 'helmet_light': '#BEC3C5', 'accent': '#808080'}, 'LAC': {'name': 'CHARGERS', 'jersey': '#0080c6', 'highlight': '#52A9D8', 'helmet': '#FFFFFF', 'helmet_light': '#FFFFFF', 'accent': '#80C0E2'}, 'LAR': {'name': 'RAMS', 'jersey': '#003594', 'highlight': '#5276B6', 'helmet': '#003594', 'helmet_light': '#476EB2', 'accent': '#809ACA'}, 'MIA': {'name': 'DOLPHINS', 'jersey': '#008e97', 'highlight': '#52B2B8', 'helmet': '#FFFFFF', 'helmet_light': '#FFFFFF', 'accent': '#80C6CB'}, 'MIN': {'name': 'VIKINGS', 'jersey': '#4f2683', 'highlight': '#876BAB', 'helmet': '#4F2683', 'helmet_light': '#8063A6', 'accent': '#A792C1'}, 'NE': {'name': 'PATRIOTS', 'jersey': '#002a5c', 'highlight': '#526E90', 'helmet': '#B0B7BC', 'helmet_light': '#C6CBCF', 'accent': '#8094AE'}, 'NO': {'name': 'SAINTS', 'jersey': '#d3bc8d', 'highlight': '#E1D1B1', 'helmet': '#D3BC8D', 'helmet_light': '#DFCFAD', 'accent': '#E9DEC6'}, 'NYG': {'name': 'GIANTS', 'jersey': '#003c7f', 'highlight': '#527AA8', 'helmet': '#003C7F', 'helmet_light': '#4773A3', 'accent': '#809EBF'}, 'NYJ': {'name': 'JETS', 'jersey': '#115740', 'highlight': '#5D8D7D', 'helmet': '#115740', 'helmet_light': '#548675', 'accent': '#88ABA0'}, 'PHI': {'name': 'PHILADELPHIA', 'jersey': '#06424d', 'highlight': '#567E86', 'helmet': '#06424D', 'helmet_light': '#4C777F', 'accent': '#82A0A6'}, 'PIT': {'name': 'STEELERS', 'jersey': '#24242C', 'highlight': '#525252', 'helmet': '#171717', 'helmet_light': '#585858', 'accent': '#808080'}, 'SF': {'name': '49ERS', 'jersey': '#aa0000', 'highlight': '#C55252', 'helmet': '#B3995D', 'helmet_light': '#C8B68A', 'accent': '#D48080'}, 'SEA': {'name': 'SEAHAWKS', 'jersey': '#002a5c', 'highlight': '#526E90', 'helmet': '#002A5C', 'helmet_light': '#47668A', 'accent': '#8094AE'}, 'TB': {'name': 'BUCCANEERS', 'jersey': '#bd1c36', 'highlight': '#D26576', 'helmet': '#7A7067', 'helmet_light': '#9F9892', 'accent': '#DE8E9A'}, 'TEN': {'name': 'TITANS', 'jersey': '#4495d2', 'highlight': '#80B7E0', 'helmet': '#001532', 'helmet_light': '#47576B', 'accent': '#A2CAE8'}, 'WSH': {'name': 'COMMANDERS', 'jersey': '#5a1414', 'highlight': '#8F5F5F', 'helmet': '#5A1414', 'helmet_light': '#885656', 'accent': '#AC8A8A'}}

def main(config):
    team=config.get('team','PHI').upper()
    style=STYLES.get(team,STYLES['PHI'])
    frames=[scene(n,style) for n in range(20)]
    banner=render.Box(width=64,height=32,color='#000000',child=render.Column(cross_align='center',children=[render.Text(content='TOUCHDOWN!',font='CG-pixel-4x5-mono',color='#FFFFFF'),render.Box(width=1,height=4),render.Text(content=style['name'],font='CG-pixel-3x5-mono',color=style['accent'])]))
    return render.Root(delay=130,child=render.Animation(children=frames+[banner for i in range(9)]))
