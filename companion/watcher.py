"""Local, at-most-once NFL touchdown notifications. Python standard library only."""
import base64,datetime,json,logging,os,pathlib,sqlite3,time,urllib.request
from decimal import Decimal,InvalidOperation
from logging.handlers import RotatingFileHandler
LOG=logging.getLogger('touchdown')
BASE='https://site.api.espn.com/apis/site/v2/sports/football/nfl/'

def integer(value):
    if isinstance(value,bool) or value is None: return None
    try:
        n=Decimal(str(value))
        return int(n) if n.is_finite() and n==n.to_integral_value() else None
    except (InvalidOperation,ValueError,OverflowError): return None

def ident(value):
    n=integer(value)
    return str(n) if n is not None and n>=0 else None

def timestamp(value):
    try:return datetime.datetime.fromisoformat(value.replace('Z','+00:00')).timestamp()
    except (AttributeError,ValueError):return None

def request(url,body=None,key=None,method=None):
    headers={}
    if key:headers['Authorization']='Bearer '+key
    if body is not None:headers['Content-Type']='application/json'
    req=urllib.request.Request(url,data=json.dumps(body).encode() if body is not None else None,headers=headers,method=method)
    with urllib.request.urlopen(req,timeout=12) as r:
        data=r.read()
    try:return json.loads(data)
    except json.JSONDecodeError:return data.decode()

def scoring(summary):
    # Only explicit scoring records identify the scoring team reliably on defensive TDs.
    clocks={}
    drives=summary.get('drives',{})
    all_drives=list(drives.get('previous',[]))
    if drives.get('current'):all_drives.append(drives['current'])
    for drive in all_drives:
        for play in drive.get('plays',[]):clocks[ident(play.get('id'))]=timestamp(play.get('wallclock'))
    result={}
    for play in summary.get('scoringPlays',[]):
        pid=ident(play.get('id'))
        if not pid or play.get('scoringType',{}).get('name')!='touchdown':continue
        team=play.get('team',{}).get('abbreviation','').upper()
        if not team:continue
        scores=[integer(play.get('awayScore')),integer(play.get('homeScore'))]
        if any(v is None or v<0 for v in scores):continue
        result[pid]={'id':pid,'team':team,'scores':scores,'wallclock':clocks.get(pid)}
    return result

def observe(state,game,summary,now):
    """Two consistent polls; baseline startup/gaps; never infer from score deltas."""
    plays=scoring(summary)
    old=state.get(game)
    if old is None or now-old.get('last',0)>180:
        state[game]={'seen':list(plays),'pending':{},'last':now}
        return []
    seen=set(old['seen']);pending=old['pending'];events=[]
    comp=summary.get('header',{}).get('competitions',[{}])[0]
    status=comp.get('status',{}).get('type',{})
    active=status.get('state')=='in' and status.get('name') not in ('STATUS_POSTPONED','STATUS_SUSPENDED','STATUS_CANCELED')
    for pid,play in plays.items():
        if pid in seen:continue
        wall=play['wallclock']
        if not active or (wall is not None and not -30<=now-wall<=180):
            seen.add(pid);continue
        prior=pending.get(pid)
        signature=[play['team'],play['scores']]
        if prior and prior['signature']==signature and 10<=now-prior['first']<=120:
            events.append(play);seen.add(pid)
        elif not prior or prior['signature']!=signature:
            pending[pid]={'first':now,'signature':signature}
        elif now-prior['first']>120:seen.add(pid)
    old.update(seen=sorted(seen),pending={k:v for k,v in pending.items() if k in plays and k not in seen},last=now)
    return events

def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data));tmp.chmod(0o600);tmp.replace(path)

def device_key(data,device):
    with sqlite3.connect('file:'+str(data/'tronbyt.db')+'?mode=ro',uri=True) as c:
        row=c.execute('select api_key from devices where id=?',(device,)).fetchone()
    if not row:raise RuntimeError('Configured device missing')
    return row[0]


def enabled(value,default=True):
    if value is None:return default
    return str(value).lower() in ('true','1')

def settings(data,device):
    with sqlite3.connect('file:'+str(data/'tronbyt.db')+'?mode=ro',uri=True) as c:
        row=c.execute('select config,enabled,path,empty_last_render from apps where device_id=? and iname=?',(device['id'],device['installation'])).fetchone()
    if not row:raise ValueError('Configured installation does not exist')
    if pathlib.PurePosixPath(row[2] or '').name!='retro_nfl.star':raise ValueError('Configured installation is not Retro NFL')
    options=json.loads(row[0] or '{}')
    team=str(options.get('team','PHI')).upper()
    if team not in TEAMS:raise ValueError('Unknown team selection')
    return {'team':team,'focus':enabled(options.get('game_focus')),'celebrate':options.get('celebrate','either'),'enabled':bool(row[1]),'render_ok':not bool(row[3])}

TEAMS=set('ARI ATL BAL BUF CAR CHI CIN CLE DAL DEN DET GB HOU IND JAX KC LV LAC LAR MIA MIN NE NO NYG NYJ PHI PIT SF SEA TB TEN WSH'.split())

def may_celebrate(prefs,play):
    return prefs['celebrate']=='either' or (prefs['celebrate']=='favorite' and play['team']==prefs['team'])

def recent_render(app,now):
    try:return now-float(app.get('lastRenderAt',0))<180
    except (ValueError,TypeError):return False

def focus_action(owned,current,target,live,allowed,healthy):
    """Never replace another manual pin; only release a pin this service acquired."""
    if owned and str(current or '')!=target:return 'forget'
    if owned and (not live or not allowed):return 'release'
    if not owned and not current and live and allowed and healthy:return 'acquire'
    return None

def focus(cfg,device,prefs,live,owned,statepath,state):
    did=device['id'];target=device['installation'];key=device_key(cfg['data'],did)
    url=cfg['server']+'/v0/devices/'+did
    status=request(url,key=key)
    app=request(url+'/installations/'+target,key=key)
    current=status.get('pinnedApp')
    now=time.time()
    online=timestamp(status.get('lastSeen'))
    allowed=prefs['enabled'] and prefs['focus'] and not status.get('nightMode',{}).get('active')
    healthy=online is not None and now-online<90 and recent_render(app,now) and prefs['render_ok']
    action=focus_action(did in owned,current,target,live,allowed,healthy)
    if action=='forget':
        owned.pop(did,None);save(statepath,state)
    elif action=='release':
        request(url+'/installations/'+target,{'pinned':False},key,method='PATCH')
        owned.pop(did,None);save(statepath,state)
    elif action=='acquire':
        # Record ownership before the request so a restart can release an accepted pin.
        owned[did]=target;save(statepath,state)
        request(url+'/installations/'+target,{'pinned':True},key,method='PATCH')
    return status

def deliver(cfg,device,play):
    did=device['id'];target=device['installation'];key=device_key(cfg['data'],did)
    url=cfg['server']+'/v0/devices/'+did
    prefs=settings(cfg['data'],device)
    if not prefs['enabled'] or not prefs['render_ok'] or not may_celebrate(prefs,play):return False
    status=request(url,key=key)
    seen=timestamp(status.get('lastSeen'))
    if status.get('nightMode',{}).get('active') or seen is None or time.time()-seen>90:return False
    if status.get('pinnedApp') and str(status['pinnedApp'])!=target:return False
    app=request(url+'/installations/'+target,key=key)
    if not app.get('enabled') or not recent_render(app,time.time()):return False
    files=list((cfg['data']/'webp'/did).glob('*-'+target+'.webp'))
    if not files:return False
    board=max(files,key=lambda f:f.stat().st_mtime)
    if time.time()-board.stat().st_mtime>180:return False
    asset=cfg['assets']/(play['team']+'.webp')
    if not asset.is_file():return False
    request(url+'/push',{'image':base64.b64encode(asset.read_bytes()).decode(),'background':False},key)
    time.sleep(3.8)
    request(url+'/push',{'image':base64.b64encode(board.read_bytes()).decode(),'background':False},key)
    LOG.info('Delivered touchdown to configured display')
    return True

def validate_devices(devices):
    if not isinstance(devices,list) or not devices:raise ValueError('Configure at least one display')
    seen=set()
    for d in devices:
        for key in ('id','installation'):
            value=d.get(key)
            if not isinstance(value,str) or not value or not all(c.isalnum() or c in '-_' for c in value):raise ValueError('Invalid device/installation identifier')
        if d['id'] in seen:raise ValueError('Only one managed installation per display')
        seen.add(d['id'])
    return devices

def run():
    root=pathlib.Path(__file__).resolve().parent
    cfg={'server':os.environ['TRONBYT_URL'].rstrip('/'),'data':pathlib.Path(os.environ.get('TRONBYT_DATA','/tronbyt-data')),'assets':root/'assets'}
    devices=validate_devices(json.loads(pathlib.Path(os.environ.get('DEVICES_FILE','/config/devices.json')).read_text()))
    statepath=pathlib.Path(os.environ.get('STATE_PATH','/state/state.json'))
    state=json.loads(statepath.read_text()) if statepath.exists() else {'games':{},'owned':{}}
    for v in state['games'].values():v['last']=0
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(message)s')
    LOG.info('Retro NFL companion started for %d configured displays',len(devices))
    while True:
        delay=60
        try:
            now=time.time();today=datetime.datetime.now(datetime.timezone.utc)
            events={}
            for day in (today-datetime.timedelta(days=1),today):
                feed=request(BASE+'scoreboard?dates='+day.strftime('%Y%m%d')+'&limit=100')
                if not isinstance(feed.get('events'),list):raise ValueError('Invalid scoreboard response')
                for e in feed['events']:events[str(e['id'])]=e
            prefs={d['id']:settings(cfg['data'],d) for d in devices}
            active={d['id']:False for d in devices}
            for event in events.values():
                c=event.get('competitions',[{}])[0]
                teams={t.get('team',{}).get('abbreviation') for t in c.get('competitors',[])}
                targets=[d for d in devices if prefs[d['id']]['enabled'] and prefs[d['id']]['team'] in teams]
                if not targets:continue
                kickoff=timestamp(event.get('date'))
                if kickoff is None or not -1800<now-kickoff<25200:continue
                kind=c.get('status',{}).get('type',{})
                live=kind.get('state')=='in' and not kind.get('completed') and kind.get('name') not in ('STATUS_SUSPENDED','STATUS_DELAYED','STATUS_CANCELED','STATUS_POSTPONED')
                if not live:continue
                delay=10
                for d in targets:active[d['id']]=True
                game=ident(event.get('id'))
                if not game:continue
                summary=request(BASE+'summary?event='+game)
                plays=observe(state['games'],game,summary,now)
                save(statepath,state)
                for play in plays:
                    for d in targets:
                        try:deliver(cfg,d,play)
                        except Exception as exc:LOG.warning('Delivery failed (%s); no retry',type(exc).__name__)
            for d in devices:
                try:focus(cfg,d,prefs[d['id']],active[d['id']],state['owned'],statepath,state)
                except Exception as exc:LOG.warning('Focus check failed (%s)',type(exc).__name__)
            save(statepath,state)
            save(statepath.parent/'health.json',{'lastSuccessfulPoll':time.time()})
        except Exception as exc:
            LOG.warning('Poll failed (%s); leaving displays unchanged',type(exc).__name__)
        time.sleep(delay)

if __name__=='__main__':run()
