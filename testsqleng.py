# encoding: utf-8
import unittest
import sys
import datetime
from datetime import date
import calendar
from datetime import timedelta
from test.datetimetester import DAY

sys.path.append(r'c:\sbis\inside\www\service\Модули\Python')
sys.path.append(r'C:\sbis\inside\core-edo\www\service\Модули\Сотрудники')

sys.path.append(r'c:\sbis\inside\www\service\Модули\Зарплата и Кадры')




from SqlEngine import *

class TestSql(unittest.TestCase):
    def test_arr(self):
                ДолжностьСотрудника12 = Table("ДолжностьСотрудника12","ДолжностьСотрудника12")
                print (Select(ДолжностьСотрудника12.Сотрудник[2]).Where(ДолжностьСотрудника12.Сотрудник == ДолжностьСотрудника12.Сотрудник[2] ))
    def _test_convert(self): 
                
                ДолжностьСотрудника1 = Table("ДолжностьСотрудника1","ДолжностьСотрудника1")
                ДолжностьСотрудника = Table("ДолжностьСотрудника","ДолжностьСотрудника")
                ДолжностьСотрудника12 = Table("ДолжностьСотрудника12","ДолжностьСотрудника12")
                print (Select(ДолжностьСотрудника12.Сотрудник[2]))
                sel_job = Select(Column(ДолжностьСотрудника,"@ДолжностьСотрудника"))\
                            .From(ДолжностьСотрудника)\
                            .LeftJoin(ДолжностьСотрудника1,(ДолжностьСотрудника1.Сотрудник ==  ДолжностьСотрудника.Сотрудник ))\
                            .LeftJoin(ДолжностьСотрудника12,(ДолжностьСотрудника12.Сотрудник ==  ДолжностьСотрудника.Сотрудник ))\
                            .Where((ДолжностьСотрудника12.Сотрудник == 22)&(1==1) )\
                            .Limit(1)
                sel_job = sel_job.converToWithConstruction()            
                print(sel_job) 
                 
    def _test_Sql1(self): 
                ДолжностьСотрудника = Table("ДолжностьСотрудника","ДолжностьСотрудника")
                sel_job = Select(Column(ДолжностьСотрудника,"@ДолжностьСотрудника"))\
                            .From(ДолжностьСотрудника)\
                            .Where(ДолжностьСотрудника.Сотрудник == 22)\
                            .OrderBy(ДолжностьСотрудника.ДатаСнятия.desc.nulls.first)\
                            .Limit(1)
                print(sel_job)               
    def _test_Sql(self):
        
        
        self.ЧастноеЛицо = Table("ЧастноеЛицо","ЧастноеЛицо")
        base = Table("Привет")

        sfsf = Table("sfsf")

        col = self.ЧастноеЛицо.Фамилия + "' '" + self.ЧастноеЛицо.Имя + Coalesce(Text("' '") +  self.ЧастноеЛицо.Отчество,"''")  + Coalesce(Text("' '") + self.ЧастноеЛицо.Телефон, "''" ) + Coalesce(Text("' '") + self.ЧастноеЛицо.МобильныйТелефон, "''" ) 
            
        print(str(col))
        d =  Select(Coalesce(base.sd,"d"),"fff", "ffff")
        
        
        
        q  = Select(base,Count(1),Integer(Max(sfsf.ass)), Integer((Coalesce(base.sd,"d")|sfsf.ass)).as_("ssss"), d.as_("asad"),Column().setValue(1).as_("eee"), Column().setValue("dddd").as_("eee"), sfsf.ass.as_('FirstName') , base.sd)\
            .From(base)\
           .Where((sfsf.ass.like("'%3dd'")) &(sfsf.ass >  base.sd) & (sfsf.ass ==  base.sd) & (sfsf.ass.in_(d)))\
           .InnerJoin(sfsf,(sfsf.ass !=  None )& (sfsf.ass !=  False ) & ((sfsf.ass !=  base.sd) | (sfsf.ass ==  base.sd)) & ((sfsf.ass.in_([0, 2])) | (sfsf.ass == Any([0, 1]))))\
            
        un = Select(Distinct(Coalesce(base.sd,"d")).as_("eee"),"fff", "ffff").Union(Select(Coalesce(base.sd,"d"),"fff", "ffff"))
        print(un )
        where = q.getWhere()
        q.setWhere(where & (sfsf.aaaaaaaa ==  base.bbbbbbbbb) )     
        
        col = q.getColumns()
        #print(col)
        col.append(sfsf.df1)
        #print(col)
        table = q.getTableByName("sfsf")
        #print(table)
        #print(table.getCondition())
        print(q)
        #print(q.FirstName)
        
        e = With(d.as_("АА"))\
            .Select("*").From(d)
        print(e)


        t = RecFunction("getID")
        es = With_Recursive(t).As(Select(d.asa).From(base).Union(Select(t.asa).From(t).Where(t.ee == d.ee))).Select('*').From(t)
        print(es)


if __name__ == '__main__':
    unittest.main()
    