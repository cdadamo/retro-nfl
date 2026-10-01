import copy,unittest
from watcher import integer,ident,observe

def summary(plays,state='in'):
 return {'header':{'competitions':[{'status':{'type':{'state':state}}}]},'scoringPlays':plays}
def td(pid='123',team='PHI',score=7):
 return {'id':pid,'team':{'abbreviation':team},'awayScore':score,'homeScore':0,'scoringType':{'name':'touchdown'}}
class Tests(unittest.TestCase):
 def test_numbers(self):
  for x in (1,1.0,'1','1.0'):self.assertEqual(integer(x),1);self.assertEqual(ident(x),'1')
  for x in (None,True,'bad','NaN',1.5,'Infinity'):self.assertIsNone(integer(x))
 def state(self):
  s={};observe(s,'game',summary([]),1000);return s
 def test_once(self):
  s=self.state();j=summary([td()]);self.assertEqual(observe(s,'game',j,1020),[])
  self.assertEqual(len(observe(s,'game',j,1040)),1)
  self.assertEqual(observe(s,'game',j,1060),[])
 def test_restart_or_gap(self):
  s={};j=summary([td()]);self.assertEqual(observe(s,'g',j,1000),[])
  self.assertEqual(observe(s,'g',summary([td(),td('124')]),1400),[])
 def test_float_equivalence(self):
  s=self.state();observe(s,'game',summary([td(123.0,score='7.0')]),1020)
  self.assertEqual(len(observe(s,'game',summary([td('123.0',score=7)]),1040)),1)
  self.assertEqual(observe(s,'game',summary([td(123,score=7.0)]),1060),[])
 def test_non_touchdowns(self):
  s=self.state();p=td();p['scoringType']['name']='field-goal'
  self.assertEqual(observe(s,'game',summary([p]),1020),[])
  self.assertEqual(observe(s,'game',summary([p]),1040),[])
 def test_retracted(self):
  s=self.state();observe(s,'game',summary([td()]),1020)
  self.assertEqual(observe(s,'game',summary([]),1040),[])
  self.assertEqual(s['game']['pending'],{})
 def test_final(self):
  s=self.state();observe(s,'game',summary([td()]),1020)
  self.assertEqual(observe(s,'game',summary([td()],'post'),1040),[])
 def test_team_change(self):
  s=self.state();observe(s,'game',summary([td(team='PHI')]),1020)
  self.assertEqual(observe(s,'game',summary([td(team='CHI')]),1040),[])
  self.assertEqual(observe(s,'game',summary([td(team='CHI')]),1060)[0]['team'],'CHI')
 def test_old_wallclock(self):
  s=self.state();j=summary([td()]);j['drives']={'previous':[{'plays':[{'id':'123','wallclock':'1970-01-01T00:00:01Z'}]}]}
  self.assertEqual(observe(s,'game',j,1020),[]);self.assertEqual(observe(s,'game',j,1040),[])
if __name__=='__main__':unittest.main()
