import json,pathlib,sqlite3,tempfile,unittest
from unittest.mock import patch
import watcher
class Settings(unittest.TestCase):
 def test_preferences_from_installed_app(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   c=sqlite3.connect(root/'tronbyt.db');c.execute('create table apps(device_id text,iname text,config text,enabled int,path text,empty_last_render int)')
   c.execute('insert into apps values(?,?,?,?,?,?)',('screen','123',json.dumps({'team':'CHI','game_focus':'false','celebrate':'favorite'}),1,'retronfl/retro_nfl.star',0));c.commit();c.close()
   p=watcher.settings(root,{'id':'screen','installation':'123'})
   self.assertEqual(p,{'team':'CHI','focus':False,'celebrate':'favorite','enabled':True,'render_ok':True})
 def test_favorite_only(self):
  p={'team':'CHI','celebrate':'favorite'}
  self.assertTrue(watcher.may_celebrate(p,{'team':'CHI'}));self.assertFalse(watcher.may_celebrate(p,{'team':'PHI'}))
  p['celebrate']='either';self.assertTrue(watcher.may_celebrate(p,{'team':'PHI'}))
 def test_focus_ownership(self):
  f=watcher.focus_action
  self.assertEqual(f(False,None,'123',True,True,True),'acquire')
  self.assertIsNone(f(False,'other','123',True,True,True))
  self.assertIsNone(f(False,'123','123',False,False,True))
  self.assertEqual(f(True,'123','123',False,True,True),'release')
  self.assertEqual(f(True,'123','123',True,False,True),'release')
  self.assertEqual(f(True,'other','123',True,True,True),'forget')
  self.assertIsNone(f(False,None,'123',True,True,False))
 def test_validation(self):
  self.assertEqual(len(watcher.validate_devices([{'id':'screen','installation':'123'}])),1)
  for d in [[{'id':'../secret','installation':'123'}],[{'id':'a','installation':'123'},{'id':'a','installation':'456'}]]:
   with self.assertRaises(ValueError):watcher.validate_devices(d)
if __name__=='__main__':unittest.main()
