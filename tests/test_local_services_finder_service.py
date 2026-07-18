import unittest
from datetime import date,timedelta
from types import SimpleNamespace
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.modules.local_services_finder.db import Base
from app.modules.local_services_finder.schemas import CategoryCreate,ProviderCreate
from app.modules.local_services_finder.service import archive,dashboard,delete_category,delete_provider,get_provider,list_categories,list_providers,restore,save_category,save_provider,set_preferred
class LocalServicesFinderTests(unittest.TestCase):
 def setUp(self):
  e=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool);Base.metadata.create_all(e);self.db=sessionmaker(bind=e)();self.a=SimpleNamespace(id="a");self.b=SimpleNamespace(id="b");self.cat=save_category(self.db,self.a,CategoryCreate(name="Electrician",color="blue",sortOrder=1))
 def tearDown(self):self.db.close()
 def make(self,**kw):
  data=dict(businessName="Bright Fix",categoryId=self.cat.id,contactPerson="Ali",phone="+971 50 123 4567",alternatePhone=None,email="team@example.com",website="https://example.com",address="Street 1",city="Dubai",area="Marina",notes="Trusted",rating=5,preferred=True,lastContacted=date.today());data.update(kw);return save_provider(self.db,self.a,ProviderCreate(**data))
 def test_validation_duplicate_ownership_search_filters_dashboard(self):
  bad=[dict(businessName=" "),dict(businessName="x",phone="bad*phone"),dict(businessName="x",email="bad"),dict(businessName="x",website="example.com"),dict(businessName="x",rating=6)]
  for p in bad:
   with self.assertRaises(ValidationError):ProviderCreate(**p)
  p=self.make();self.assertEqual(p.category_name,"Electrician");self.assertTrue(p.preferred)
  with self.assertRaises(HTTPException):self.make(businessName="bright fix")
  with self.assertRaises(HTTPException):get_provider(self.db,self.b,p.id)
  found=list_providers(self.db,self.a,"bright",self.cat.id,True,False,5,date.today()-timedelta(days=1),date.today()+timedelta(days=1),1,10);self.assertEqual(found.total,1)
  summary=found.items[0]
  self.assertNotIn("alternate_phone",summary.model_dump())
  self.assertNotIn("email",summary.model_dump())
  self.assertNotIn("website",summary.model_dump())
  d=dashboard(self.db,self.a);self.assertEqual(d.providers,1);self.assertEqual(d.preferred,1);self.assertEqual(d.recently_contacted,1);self.assertEqual(d.categories,1)
  with self.assertRaises(HTTPException):list_providers(self.db,self.a,last_contacted_from=date.today(),last_contacted_to=date.today()-timedelta(days=1))
 def test_archive_restore_preferred_category_delete(self):
  p=self.make(preferred=False,rating=3);p=set_preferred(self.db,self.a,p.id,True);self.assertTrue(p.preferred)
  p=archive(self.db,self.a,p.id);self.assertTrue(p.archived)
  with self.assertRaises(HTTPException):save_provider(self.db,self.a,ProviderCreate(businessName="Blocked"),p.id)
  with self.assertRaises(HTTPException):delete_provider(self.db,self.a,p.id)
  p=restore(self.db,self.a,p.id);self.assertFalse(p.archived)
  with self.assertRaises(HTTPException):delete_category(self.db,self.a,self.cat.id)
  delete_provider(self.db,self.a,p.id);delete_category(self.db,self.a,self.cat.id);self.assertEqual(list_categories(self.db,self.a).total,0)
if __name__=="__main__":unittest.main()
