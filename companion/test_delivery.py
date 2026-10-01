import base64,datetime,json,pathlib,tempfile,time,unittest
from unittest.mock import patch
import watcher
class Delivery(unittest.TestCase):
 def run_case(self,night=False,pin=None,own_only=False,stale=False,fail=False):
  calls=[]
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'webp'/'screen').mkdir(parents=True);(root/'assets').mkdir()
   (root/'webp'/'screen'/'Retro NFL-123.webp').write_bytes(b'score');(root/'assets'/'CHI.webp').write_bytes(b'touchdown')
   cfg={'server':'http://example.invalid','data':root,'assets':root/'assets'}
   def request(url,body=None,key=None,method=None):
    if body is not None:
     calls.append(body)
     if fail:raise TimeoutError()
     return 'ok'
    if '/installations/' in url:return {'enabled':True,'lastRenderAt':0 if stale else time.time()}
    return {'nightMode':{'active':night},'lastSeen':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pinnedApp':pin}
   with patch.object(watcher,'settings',return_value={'team':'PHI','celebrate':'favorite' if own_only else 'either','enabled':True,'render_ok':True}),patch.object(watcher,'device_key',return_value='test'),patch.object(watcher,'request',side_effect=request),patch.object(watcher.time,'sleep'):
    try:watcher.deliver(cfg,{'id':'screen','installation':'123'},{'team':'CHI'})
    except TimeoutError:pass
  return calls
 def test_overlay_return(self):
  calls=self.run_case(pin='123');self.assertEqual(len(calls),2)
  self.assertEqual(base64.b64decode(calls[0]['image']),b'touchdown')
  self.assertEqual(base64.b64decode(calls[1]['image']),b'score')
  self.assertEqual(set(calls[0]),{'image','background'})
 def test_no_interrupt_sleep_or_manual_pin(self):
  self.assertEqual(self.run_case(night=True),[]);self.assertEqual(self.run_case(pin='other'),[])
 def test_favorite_only_and_stale(self):
  self.assertEqual(self.run_case(own_only=True),[]);self.assertEqual(self.run_case(stale=True),[])
 def test_ambiguous_failure_never_retries(self):self.assertEqual(len(self.run_case(fail=True)),1)
if __name__=='__main__':unittest.main()
