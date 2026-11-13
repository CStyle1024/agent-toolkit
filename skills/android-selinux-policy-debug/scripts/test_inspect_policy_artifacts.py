import hashlib,json,subprocess,sys,tempfile,unittest
from pathlib import Path
SCRIPT=Path(__file__).with_name("inspect_policy_artifacts.py")
class InspectorTests(unittest.TestCase):
 def run_tool(self,*files,service='assistant_guard'):
  cmd=[sys.executable,str(SCRIPT),'--type','assistant_guard_service','--service',service,*map(str,files)]
  r=subprocess.run(cmd,capture_output=True,text=True)
  self.assertNotEqual(r.returncode,2,r.stderr)
  return r,json.loads(r.stdout)
 def test_old_new_and_identical_content(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);old=root/'old.cil';new=root/'new.cil';copy=root/'copy.cil'
   old.write_bytes(b'(type window_service)\n');new.write_bytes(b'(type assistant_guard_service)\n');copy.write_bytes(old.read_bytes())
   r,data=self.run_tool(old,new,copy)
   self.assertEqual(r.returncode,0)
   self.assertEqual([f['type_name_occurrences'] for f in data['files']],[0,1,0])
   self.assertEqual(data['files'][0]['sha256'],hashlib.sha256(old.read_bytes()).hexdigest())
   self.assertEqual(data['identical_file_groups'],[[str(old),str(copy)]])
 def test_mapping_is_exact_and_preserves_mismatch(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'product_service_contexts'
   f.write_text('# assistant_guard u:object_r:assistant_guard_service:s0\nassistant_guard_old u:object_r:assistant_guard_service:s0\nassistant_guard u:object_r:wrong_service:s0\nassistant_guard u:object_r:assistant_guard_service:s0 # duplicate\n')
   r,data=self.run_tool(f)
   matches=data['files'][0]['exact_service_mappings']
   self.assertEqual([m['line'] for m in matches],[3,4])
   self.assertEqual([m['matches_target_type'] for m in matches],[False,True])
 def test_missing_file_is_not_absent_type(self):
  with tempfile.TemporaryDirectory() as d:
   r,data=self.run_tool(Path(d)/'missing')
   self.assertEqual(r.returncode,1)
   self.assertEqual(data['files'][0]['status'],'read_error')
   self.assertNotIn('type_name_occurrences',data['files'][0])
 def test_binary_occurrence_does_not_report_permission(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'policy';f.write_bytes(b'\x00assistant_guard_service\x00')
   r,data=self.run_tool(f)
   self.assertEqual(data['files'][0]['type_name_occurrences'],1)
   self.assertNotIn('allow',data['files'][0])
   self.assertNotIn('exact_service_mappings',data['files'][0])
if __name__=='__main__':unittest.main()
