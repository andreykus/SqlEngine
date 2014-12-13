# encoding: utf-8
'''
@author: av.Kustov
'''
import copy
from collections import OrderedDict

NoneToString = lambda par: "" if par is None else par

class Shema:
    """
    Схема БД
    """
    shema = ''
class Expression(object):
    """
    класс элемента - Выражение
    """
    def __init__(self):
        self._tables_ = []
    def __str__(self):
        return ""
        #raise NotImplementedError
    def __hash__(self):
        return hash(str(self))
    @property
    def params(self):
        raise NotImplementedError
  
    def as_(self, output_name):
        """
        выражение AS
        :param output_name:
        """
        return As(self, output_name)
    
    def in_(self, values):
        """
        выражение IN
        :param values:
        """
        return In(self, values)
    
    def not_in_(self, values):
        """
        выражение Not IN
        :param values:
        """
        return NotIn(self, values)

    
    def __lt__(self, other): #- x < y вызывает x.__lt__(y).
        return Less(self, other)
    def __le__(self, other): #- x <= y вызывает x.__le__(y).
        return LessEqual(self, other)
    def __gt__(self, other): #- x > y вызывает x.__gt__(y).
        return Greater(self, other)
    def __ge__(self, other): #- x >= y вызывает x.__ge__(y).
        return GreaterEqual(self, other)
    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __mul__(self, other):
        return Mul(self, other)

    def __div__(self, other):
        return Div(self, other)


    def __and__(self, other):
        """
        выражение AND
        :param other:
        """
        return AND(self,other)

    def __eq__(self, other):
        """
        выражение =
        :param other:
        """
        return Equals(self, other)
    
    def __ne__(self, other):
        """
        выражение !=
        :param other:
        """
        return NotEqual(self, other)
    
    def __or__(self, other):
        """
        выражение OR
        :param other:
        """
        return OR(self, other)

    @property
    def asc(self):
        return Asc(self)

    @property
    def desc(self):
        return Desc(self)
    
    @property
    def nulls(self):
        return Nulls(self)

    @property
    def first(self):
        return First(self)
   
    @property
    def last(self):
        return Last(self) 
    
    
    def like(self, test):
        return Like(self, test)

    def ilike(self, test):
        return ILike(self, test)
    
    def find_type_object(self, type, comparator = None , setobject = None):
        """
        поиск объекта выражения по
        :param comparator: условию - Компаратор
        :param setobject: заменить объектом если уд. условию
        :param type: типу объекта
        """
        ret = []
        def check(atrib, attr = None):
            """
            Компаратор проверки объекта условиям
            :param atrib: атрибут
            :param attr: название атрибута
            """
            if comparator is not None and setobject is not None:
                if comparator(atrib):
                    ret.append(atrib)
                    if attr is not None:
                        setattr(self, attr, setobject)
            elif comparator is None and setobject is not None: 
                ret.append(atrib)
                if attr is not None:
                        setattr(self, attr, setobject)           
            elif comparator is not None:
                if comparator(atrib):
                    ret.append(atrib)
            else:
                ret.append(atrib)

        if isinstance(self, type):
            check(self)
        else:
            for attr in dir(self):
                if attr  in ['asc','desc','first','last','nulls', 'params']: continue
                atrib = getattr(self, attr)
                if isinstance(atrib,type):
                    check(atrib,attr)
                elif isinstance(atrib,(Expression)):
                    if isinstance(atrib,(Coalesce,Is,Not)):
                        for  at_i in  atrib.values:
                            if not isinstance(at_i,Expression) :continue
                            ret_obj = at_i.find_type_object(type, comparator, setobject )                    
                            ret = ret + ret_obj
                    else:                        
                        ret_obj = atrib.find_type_object(type, comparator, setobject )                    
                        ret = ret + ret_obj
                elif isinstance(atrib,(Select)):
                    pass
                    #ret_obj = atrib.find_type_object(type, comparator, setobject )
                    #ret = ret + ret_obj
   
                          
        # пока так: если мы ищем колонки, и у нас пришел Distinct то его и вовращаем
        if type == Column and isinstance(self,Distinct) and len(ret)>0:
            ret = [Distinct(copy.copy(ret[0]))]

        return ret
    
class Order(Expression):
    """
    класс элемента - порядок
    """
    direct = ''

    def __init__(self, expression):
        super(Order, self).__init__()
        self.expression = expression
        # TODO USING

    def __str__(self):
        return '%s %s' % (self.expression, self.direct)

    @property
    def params(self):
        return self.expression.params


class Asc(Order):
    __slots__ = ()
    direct = 'ASC'


class Desc(Order):
    __slots__ = ()
    direct = 'DESC'
    
class Nulls(Order):
    __slots__ = ()
    direct = 'NULLS'

class First(Order):
    __slots__ = ()
    direct = 'FIRST'    

class Last(Order):
    __slots__ = ()
    direct = 'LAST'    



class Type(Expression):
    """
    класс элемента - Типы
    """
    _type = ''

    def __init__(self, expression = None):
        self.expression = expression
    def __str__(self):
        if self.expression is None and self._type == '': return  "NULL"
        if self.expression is None: return  "NULL::%s"%(self._type)
        if isinstance(self.expression , (Operator, Select)): return "(%s)::%s"%(str(self.expression),self._type) 
        return  "%s::%s"%(str(self.expression),self._type)   

class Numeric(Type):
    def  __init__(self,expression = None , ceil = None, han = None ):
        if ceil is None: ceil = 32
        self.ceil = ceil
        if han is None: han = 2
        self.han =  han
        super(Numeric,self).__init__(expression)
    def __str__(self):
        if self.expression is None: return  "NULL::numeric(%s,%d)"%(self.ceil,self.han)
        if isinstance(self.expression , (Operator, Select)): 
            return "(%s)::numeric(%s,%d)"%(str(self.expression), self.ceil, self.han)
        return str(self.expression) + "::numeric(%s,%d)"%(self.ceil,self.han)

class Uuid(Type):
    _type = "UUID" 

class Date(Type):
    _type = "date"
    
class Time(Type):
    _type = "time" 

class Regconfig(Type):
    _type = "regconfig"
    
class Integer(Type):
    _type = "integer"

class Smallint(Type):
    _type = "smallint" 

class Text(Type):
    _type = "text"

class Boolean(Type):
    _type = "boolean"
    
class MoneySQL(Type):    
    _type = "money"
    
class Duble(Type):     
    _type = "double precision"

class BigInt(Type):
    _type = "bigint"

class Operator(Expression):
    """
    класс элемента - Оператор над элеметами
    """
    _operator = ''
    def __init__(self, operand1, operand2):
        self.operand2 = operand2
        self.operand1 = operand1
    def __str__(self):
        
        return str(self.operand1) + self._operator  + str(self.operand2)
    
class Sub(Operator):
    _operator = ' - '

class Div(Operator):
    _operator = ' / '

class Add(Operator):
    isString = False
    def __init__(self, operand1, operand2):
        super(Add, self).__init__(operand1, operand2)
        self.operand2 = operand2
        self.operand1 = operand1
        self.setStr()
    def setStr(self):
        if ( (isinstance(self.operand1,(Text,Substr,Coalesce,str))) or (isinstance(self.operand2,(Text,Substr,Coalesce,str))) or (isinstance(self.operand2,(Add)) and self.operand2.isString)  or (isinstance(self.operand1,(Add)) and self.operand1.isString)):
             if isinstance(self.operand2,(Add)):  self.operand2.isString = True
             if isinstance(self.operand1,(Add)):  self.operand1.isString = True
             self.isString = True
             
    def __str__(self):
        if ( (isinstance(self.operand1,(Text,Substr,Coalesce,str))) or (isinstance(self.operand2,(Text,Substr,Coalesce,str))) or (isinstance(self.operand2,(Add)) and self.operand2.isString)  or (isinstance(self.operand1,(Add)) and self.operand1.isString)):
             return str(self.operand1) + " || " + str(self.operand2)
        return str(self.operand1) + ' + ' + str(self.operand2)

class Mul(Operator):
    _operator = ' * '

class Less(Operator):
    _operator = ' < '

class Greater(Operator):
    _operator = ' > '

class LessEqual(Operator):
    _operator = ' <= '

class GreaterEqual(Operator):
    _operator = ' >= '

class Like(Operator):
    _operator = ' LIKE '


class ILike(Operator):
    _operator = ' ILIKE '

    
class OR(Operator):
   _operator = ' OR ' 
   def __str__(self):
      if (isinstance(self.operand1, Column) or isinstance(self.operand2, Column)):
          return   '(' + str(self.operand1) + ')||( ' + str(self.operand2) + ')'
      return '(' + str(self.operand1) + ') OR (' + str(self.operand2) + ')'

class AND(Operator):
    _operator = ' AND '
    def __str__(self):
        return '('+ str(self.operand1) + ') AND (' + str(self.operand2) +')'
            
class Equals(Operator):
    def __str__(self):
        if self.operand2 is None:
            return '%s IS NULL' % self.operand1
        elif self.operand2 is True:
            return '%s IS TRUE' % self.operand1
        elif self.operand2 is False:
            return '%s IS FALSE' % self.operand1
        t1 = "%s"
        t2 = "%s"
        if isinstance(self.operand1,(Select,With)):
            t1 = "(%s)" 
        if isinstance(self.operand2,(Select,With)):
            t2 = "(%s)" 
        t = t1  + ' = ' + t2     
        return t %(str(self.operand1),str(self.operand2))

class TrueCondition(Equals):
    def __init__(self):
        super(TrueCondition, self).__init__(1,1)      

class NotEqual(Operator):
    def __str__(self):
        if self.operand2 is None:
            return '%s IS NOT NULL' % self.operand1
        elif self.operand2 is True:
            return '%s IS NOT TRUE) ' % self.operand1
        elif self.operand2 is False:
            return '%s IS NOT FALSE ' % self.operand1
        return str(self.operand1) + ' != ' + str(self.operand2)
    
class In(Operator):

    def __init__(self, operand1, inter):
        self.operand1 = operand1
        self.inter = inter    
    def __str__(self):
        if isinstance(self.inter,(list,set)): 
            return str(self.operand1) + ' IN (' + ','.join(map(str,self.inter)) + ') '
        return str(self.operand1) + ' IN (' + str(self.inter).strip('[]') + ') '

class NotIn(In):
   
    def __str__(self):
        return str(self.operand1) + ' NOT IN (' + str(self.inter).strip('[]') + ') '
    


        
class Column(Expression):
    """
    класс элемента - Колонки
    """
    def __init__(self, from_= None, name = None, value = None):
        self.alias = None
        self.__from = None
        self.__value = None
        self.__name = None
        self.__arr = None
        if  from_ is not None:
            self.__from = from_
        if  name is not None:
            self.__name = name
        if  value is not None:
            self.__value = value

    @property
    def table(self):
        return self.__from

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    def setAlias(self, alias):
        self.alias = alias
        
    def setValue(self, value):
        self.__value = value
        return self

    def setTableAndName(self,table = None ,name  = None):
        self.__from = table
        self.__name = name
    
    def __getitem__(self, val):
        self.__arr = str(val)
        return self
           
    def __str__(self):
        t = ''
        if self.__value is not None:
           if  isinstance(self.__value,str):
               t = '"%s"'
           else:
               t = '%s'
           t =  t % self.__value
           
           if self.__arr is not None:
              t = t + '[%s]' % (str(self.__arr))
           return t

        if self.__name == '*':
            t = '%s'
        else:
            t = '"%s"'
            
        if self.__from is  None :
            t = t % self.__name  
            if self.__arr is not None:
                t = t + '[%s]' % (str(self.__arr))
            return t
        alias = self.__from.alias
        if alias:
            if isinstance(self.__from, RecFunction):
                t = '%s.' + t
            else:    
                t = '"%s".' + t
            t = t % (alias, self.__name)
        else:
            t =  t % self.__name
        
        if self.__arr is not None:
            t = t + '[%s]' % (str(self.__arr))
                 
        return t

class FuncArg(Column):
    def __str__(self):
        t = '%s'
        alias = self._Column__from.alias
        if alias:
            t = '%s.' + t
            t = t % (alias, self._Column__name)
        else:
            t =  t % self._Column__name
        return t

class Table(object):
    """
    класс элемента - Таблица
    """  

    def __init__(self, tableName = None , tableAlias = None, select = None):
        self.name = None
        self.alias = None
        self.table = None
        self.name = tableName
        self.alias =  tableAlias
        self.select = select
        
    def __hash__(self):
        return hash(str(self))
    
    def __getattr__(self, name):
        return Column(self, name)

    @property
    def condition(self):
        return self.__condition

    @condition.setter
    def condition(self, value):

        if value is not None:            
           assert isinstance(value, (Expression, OR, AND))
        self.__condition = value

    def getCondition(self):
        return self.__condition

    def __str__(self):
        shema = ''
        if self.select is None:
            shema = Shema.shema
        if self.name is None:
            sql = '''{shema}"{alias}" '''.format(shema = shema, alias= NoneToString(self.alias))
        else:    
            sql = '''{shema}"{table}" "{alias}" '''.format(shema = shema, table = NoneToString(self.name), alias= NoneToString(self.alias))
        return    sql

class LeftJoin(Table):
    join = 'LEFT'
    def __init__(self,  table , condition = None):
        super(LeftJoin, self).__init__(table.name,table.alias)
        self.table = table
        if condition is not None:
            self.__condition = condition
        else:  self.__condition = table.condition
    def __str__(self):    
        sql = ''' {join} JOIN {table} ON {condition}'''.format(join = self.join, table= self.table ,
                                                           condition = str(self.__condition))
        return  sql

class InnerJoin(LeftJoin):
    join = 'INNER'
class Join(LeftJoin):
    join = ''

class Function(Expression):
    """
    класс элемента - Функция
    """
    def __init__(self):
        pass

class Any(Function):

    def __init__(self, array):
        self.array = array

    def __str__(self):
        if isinstance(self.array, (list)):
            array = 'ARRAY[' + ','.join(map(str,self.array)) + ']'
        elif isinstance(self.array, str):
            array = 'ARRAY[' + str(self.array) + ']'    
        elif isinstance(self.array, Select):
            array = 'ARRAY(' + str(self.array) + ')'  
        else :            
            array = str(self.array)    
        return ' ANY (' + str(array) + ')'
    
class Max(Function):

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return (' MAX(' +  str(self.expression) + ')')
class Lower(Function):

    def __init__(self, expression):
        self.expression = expression

    def __str__(self):
        return (' LOWER(' +  str(self.expression) + ')')
class Substr (Function): 
    def __init__(self, expression, int1, int2):
        self.expression = expression
        self.int1 =  int1
        self.int2 =  int2

    def __str__(self):
        return (' substr(' +  str(self.expression) + ','+ str(self.int1) + ',' + str(self.int2) + ')')  
class Regexp_replace(Function):

    def __init__(self, expression, string1, string2, string3 = None):
        self.expression = expression
        self.string = []
        self.string.append(string1)
        self.string.append(string2)
        if  string3 is not None:
            self.string.append(string3)

    def __str__(self):
        return (' regexp_replace( ' +  str(self.expression)+ ',' + ','.join(map(str,self.string)) + ' )')

class To_tsquery(Function):
    def __init__(self, type, expression):
        self.expression = expression
        self.type = type
    def __str__(self):
        return ' to_tsquery( ' +  str(self.type) + ' , '+ str(self.expression) +' )'

class To_tsvector(Function):
    def __init__(self, type, expression):
        if isinstance(expression,str):
             self.expression = "'%s'"%expression
        else:
            self.expression = expression
        self.type = type
        self.string = None

    def setString(self,expression):
        if isinstance(expression,str):
            self.string = "'%s'"%expression
        else:
            self.string = expression
        return self
    def __str__(self):
        vector = ' to_tsvector( ' +  str(self.type) + ' , '+ str(self.expression) +' )'
        if self.string:
            vector += ' @@ \n' + str(self.string)
        return vector

class String_agg(Function):
    def __init__(self, column, delimeter):
        self.column = column
        self.delimeter =  delimeter

    def __str__(self):
        return (' string_agg(' +  str(self.column) + ','+ self.delimeter  + ')')

class Distinct(Function):
    def __init__(self, column):
        self.column = column

    def __str__(self):
        return (' DISTINCT ' +  str(self.column))
    
class Count(Function):
    def __init__(self, expression = None):
        self.expression = expression

    def __str__(self):
        return (' COUNT(' +  str(self.expression) + ')')

class Sum(Function):
    def __init__(self, expression = None):
        self.expression = expression

    def __str__(self):
        return (' SUM(' +  str(self.expression) + ')')    

class Condidtion(Expression):
    """
    класс элемента - Условие
    """
    def __init__(self): 
        pass


class Case(Condidtion):

    def __init__(self, *whens, **kwargs):
        self.whens = whens
        self.else_ = kwargs.get('else_')

    def __str__(self):
        case = 'CASE '
        for cond, result in self.whens:
            case += 'WHEN %s THEN %s ' % (
                cond, result)
        if self.else_ is not None:
            case += 'ELSE %s ' % self.else_
        case += 'END'
        return case


class Not(Condidtion):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return ('NOT'
            + '(' + str(self.value) + ')')

class Coalesce(Condidtion):
    def __init__(self, *values):
        self.values = values

    def __str__(self):
        return ('COALESCE'
            + '(' + ', '.join(map(str, self.values)) + ')')

class Is(Condidtion):

    def __init__(self, value):
        self.values = value

    def __str__(self):
        return ('IS'
            + '(' + ', '.join(map(str, self.values)) + ')')

class Select(object):
    """
    класс конструкции SELECT
    """
    def __init__(self, *args, **kwargs ):
        self._columns = None
        self._where = None
        self._collectionTable = OrderedDict()
        self.unions = []
        self._order_By = None
        self._group_By = None
        self.limit = None
        self.offset = None
        if isinstance(args,list):
           self._columns =  args 
        else:    
           self._columns =  list(args)
        self._tables = None
        self.alias = None
        self.rev = False
        self.useSelect = None
        self.unionsAll = False
        
    def dict_copy(self, d, s= None, po = None):
        """
        копирование dict
        """
        out = OrderedDict()
        if po is None: po = len(d)
        if s is None:
            for k, v in d.iteritems():            
                out[k] = d(k)
        else:
           for i, v in enumerate(d.keys()):
                 if po >= i >= s: 
                     out[v] = d[v]     
        return out
    
    def getNameAndAlias(tables_select):
            """
            Получение пседонимов таблц
            :param tables_select:
            """
            alias_select = []
            for t in  tables_select:
                alias_select.append(t)
            return  alias_select
    
    def converToWithConstruction(self, order = None, limit = None, offset = None ):
        """
        сконвертировать простой запрос в конструкцию with        
        """     
            
        def getallTableinObject(obj):
            """
            получить все таблицы из ..
            :param obj:
            """
            tables = []
            if obj is None: return tables
            if isinstance(obj, list):
                for ob in obj:
                    tab = ob.find_type_object(Table)
                    if tab is not None:
                       tables = tables + tab
                       
            else:                    
                tables = obj.find_type_object(Table)
#             if hasattr(where, 'operand1'):
#                new_where = getattr(where, 'operand1')
#                if isinstance(new_where,(Column)):
#                     tables.append(new_where.table)                   
#                else:
#                    tables_new = getallTableinWhere(new_where)
#                    tables = tables + tables_new
#                
#             if hasattr(where, 'operand2'):
#                new_where = getattr(where, 'operand2')
#                if isinstance(new_where,(Column)):
#                    tables.append(new_where.table)
#                else:    
#                    tables_new  = getallTableinWhere(new_where) 
#                    tables = tables + tables_new        
            return tables
            
        def getStarTableIndex():
            """
            получить максимальный индекс таблицы - по котрому будем делить запрос
            """
            where = self.getWhere()
            order = self.getOrderBy()

            tables  = getallTableinObject(where) + getallTableinObject(order)
            table_index = -1
            for tabl in tables:
                aliases = list(self._collectionTable.keys())
                if tabl.alias in aliases:                    
                    if aliases.index(tabl.alias)>table_index:table_index = aliases.index(tabl.alias)                    
            return table_index
        
        def isSimple():
            """
            проверка простого запроса
            """
            is_simple = True
            if len(self.unions)>0 : is_simple = False
            return is_simple
        
        max_table_index =  getStarTableIndex()
     
        if isSimple() is not True  or (len(self._collectionTable)) == max_table_index  or max_table_index < 0 : return self       
        tables_st = self._collectionTable
        #таблицы входящие в сокращенный запрос конструкции with
        tables_select = self.dict_copy(tables_st,0,max_table_index)

        sel = Select("*").setTables(tables_select)
        sel.setWhere(self._where)

        if self.getOrderBy() is not None:
            sel.setOrderBy(copy.copy(self.getOrderBy()))
        if  self.limit is not None:
            sel.Limit(self.limit)
        if  self.offset is not None:
            sel.OffSet(self.offset)
            
            
        #таблицы входящие в конечный запрос конструкции with
        out_tables = self.dict_copy(tables_st,max_table_index + 1)
        temp_alias = "temp"

        def not_in_comp(attr):
            """
            Компаратор для поиска не входящих в конечный запрос таблиц
            :param attr:
            """
            rez = False
            if attr.alias not in out_tables.keys():
                rez = True
            return rez
        def in_comp(attr):
            """
            Компаратор для поиска входящих в конечный запрос таблиц
            :param attr:
            """
            rez = False
            if attr.alias in out_tables.keys():
                rez = True
            return rez

        def convertTables(tables,comp = not_in_comp):
            """
            Замена таблиц в конечном запросе конструкции with псевдонимом началного запроса
            :param tables:
            :param comp:
            """
            for tab in tables:
                    tabl = tables[tab]
                    new_condition = tabl._LeftJoin__condition
                    new_condition.find_type_object(Table, comp , sel)

        def convertFields(columns,comp = not_in_comp):
            """
            Замена таблиц в колонках конечного запроса конструкции with псевдонимом началного запроса
            :param columns:
            :param comp:
            """
            col_dist = None
            for column in columns:
               column.find_type_object(Table, comp ,sel)
                    
        alias_select = Select.getNameAndAlias(tables_select)

        def checkColumn(attr):
            """
            Компаратор проверки колонки для добавленния в начальный запрос (по таблицам первого запроса)
            """
            rez = False
            tab = attr.table
            val = attr.value
            if tab is not None:
                if tab.alias in alias_select:
                    rez = True
            elif val is not None:
                    pass
            return rez

        def getColumnByJoinTables(tables):
            """
            Поиск колонок для начального запроса из присоединенных таблиц конечного запросв (условия join)
            """
            columns = set()
            colum_temp = []
            for tab in tables:
                tabl = tables[tab]
                new_condition = tabl._LeftJoin__condition
                colum_temp = colum_temp + new_condition.find_type_object(Column, checkColumn)

            for col in colum_temp:
                columns.add(copy.copy(col))
            return columns

        def getColumnInSel(colun):
            """
            Поиск колонок для начального запроса из Select
            """
            columns = set()
            colum_temp = []
            
            for col in colun:
                colum_temp = colum_temp + col.find_type_object(Column, checkColumn)

            for col in colum_temp:
                columns.add(copy.copy(col))
            return columns
        
        def getColumnByOrder(order_by):
            columns = set()
            columns_temp = set()
            cols_temp = []
            for order in order_by:                
                cols_temp = cols_temp + order.find_type_object(Column)
            for col in cols_temp:
                if col.table is None:
                    columns_temp.add(col.name)
          
            for col in columns_temp:                
                col1 = self.getColumnsByAlias(col)
                if col1 is not None:
                    columns.add(col1)
            columns_out = set()   
            
                    
            for col in columns: 
               col_te =   copy.copy(col)
               col_te.output_name = col_te.output_name + '_'+ temp_alias 
               columns_out.add(copy.copy(col_te)) 
           
            cols_tab = []
            columns_out = copy.copy(columns_out)
            
            for col in columns_out:
                c = col.find_type_object(Column)
    
                for co in c:
                    def comar_col(attr):
                        """
                        Компаратор для поиска не входящих в конечный запрос таблиц
                        :param attr:
                        """
                        rez = False
                        if attr is not None and isinstance(attr, Column):
                            if attr.name == co.name:
                                rez = True 
                        return rez
                    tab = None
                    col.find_type_object(Column, comar_col ,Column(tab, co.name, None))
            
                     
            

                           
            return columns_out   
        

        def converColumnByOrder(order_by):
            columns = set()
            columns_temp = set()
            cols_temp = []
            for order in order_by:                
                cols_temp = cols_temp + order.find_type_object(Column)
            for col in cols_temp:
                if col.table is None:
                    col.setTableAndName(None, col.name + '_'+ temp_alias) 
                    
                             
        new_columns = self.getColumns()
        column_sel = getColumnInSel(new_columns)
        column_sel_in_join = getColumnByJoinTables(out_tables)
        column_in_order = getColumnByOrder(self.getOrderBy())
        converColumnByOrder(sel.getOrderBy())
        
        def udateissel(col):
            """
            в конечном запросе , в полях , которые представлены select - подменить таблицы из основного запроса
            пока так --- переделать
            """
            for c in col:
                if isinstance(c, (As)):
                    c = c.expression
                    if isinstance(c, (Type)):
                        c = c.expression
                if isinstance(c, Select):
                    alias = Select.getNameAndAlias(c.getTables())
                    def checktt(attr):
                        rez = False
                        if attr.alias not in alias and attr.alias not in out_tables.keys():
                            rez = True
                        return rez
                    
                    wh = c.getWhere()
                    wh.find_type_object(Table, checktt, sel)
        
        def udateDistinct(col):
            distCol = None
            distTabCol = None
            columns = []
            for c in col:
                if isinstance(c, Distinct):
                    distCol = c
                    distTabCol = c.column
            if distCol is not None: columns.append(distCol)    
            for c in col:
                if isinstance(c, Distinct):continue
                if str(c) == str(distTabCol): continue
                columns.append(c)
            return   columns       
                
        
        col = udateDistinct(column_sel.union(column_sel_in_join).union(column_in_order) )
        
        sel.setColumns(col)
        
        
        
        convertTables(out_tables)
        convertFields(new_columns)    
        udateissel(new_columns)
                       
        with_constr = With( sel.as_(temp_alias)).Select().setColumns(new_columns).From(sel).addTables(out_tables)
          
        return  with_constr

    def getTables(self):
        """
        вернуть все добавленные таблицы
        :return:
        """
        return self._collectionTable
    def setTables(self,tables):
        if tables is not None:
            self._collectionTable = OrderedDict(tables)
        return self
    def getTableByName(self, name):
        """
        вернуть таблицу по имени
        :return:
        """
        for table in self._collectionTable.values():
          if table.name == name: return table
        return None

    def getTableByAlias(self, alias):
        """
        вернуть таблицу по псевдониму
        :return:
        """
        return self._collectionTable.get( alias, None)

    def getWhere(self):
        """
        вернуть условие
        :return:
        """
        return self._where
      
    def getColumnsByAlias(self,alias):
        for column in self._columns:
            if isinstance(column, As) and column.output_name == alias : return column
            if isinstance(column, Column) and column.alias == alias: return column
        return None
    
    def setColumnByAlias(self,alias,expression):
        for column in self._columns:
            if isinstance(column,As) and column.output_name == alias:

                column.expression = expression
        
    def getColumns(self):
        """
        вернуть колонки выборки
        :return:
        """
        return self._columns
    def setColumns(self,columns):
        if columns is not None:
            self._columns = list(columns)
        return self
    def setAlias(self, alias):
        """
        установить псевдоним выборки
        :param alias:
        """
        self.alias = alias

    def setWhere(self, where = None):
        if where is not None:
            self._where = where
        return self
    def __getattr__(self, name):
        return Column(self, name)

    @property
    def where(self):
        return self._where

    @where.setter
    def where(self, value):
        if value is not None:
            assert isinstance(value, (Expression,OR,AND))
            self._where = value

    def generateAlias(self, nameTable):
        """
        генератор псевдонима таблицы
        :param nameTable: имя таблицы
        :return:
        """
        alias = 'A' + str(len(self._collectionTable))
        return alias

    def Where(self, value):
        """
        условие
        :return:
        """
        if value is not None:
            assert isinstance(value, (Expression,OR,AND))
            self._where = value
        return self

    def AddWhere(self, condition):
        self._where = self._where

    def Union(self, select):
        if  select is not None :
            self.unions.append(select)            
        return self
    
    def UnionAll(self, select):
        self.unionsAll = True
        if  select is not None :
            self.unions.append(select)            
        return self

    def From(self, table , useSelect = False , alias = None):
        """
        начаьная таблица
        :param Table:
        :return:
        """
        self.addTable(table,useSelect,alias)
        return self
    def addTables(self,tables):
        """
        добавить таблицы
        :param tables:
        """
        if isinstance(tables, list):
            for table in tables:
                self.addTable(table)
        else:        
            self._collectionTable.update(tables)
        return self
        
    def addTable(self, table, useSelect = None , alias = None):
        """
        добавить талицу
        :param table:
        :param useSelect:
        :param alias:
        """
        if alias is not None:
           table.alias =  alias 
        if useSelect is not None:
            table.useSelect = useSelect
        if table.alias is None:
            table.alias = self.generateAlias(table.name)
        try:
            table = self._collectionTable[table.alias]
            return table
        except KeyError :
            self._collectionTable[table.alias] = table
            return table

    def LeftJoin(self, table, condition = None):
        """
        добавить связанную таблицу
        :param table: имя таблицы
        :param condition: элемент условия
        :return: элемент таблица
        """
        if isinstance(table, Select):
            table = Table(None, table.alias, table)
        if condition is  None:
            condition =  table.__condition
        table1  = LeftJoin(table, condition)

        self.addTable(table1)
        table.alias = table1.alias
        return self

    def InnerJoin(self, table, condition = None):
        """
        добавить связанную таблицу
        :param table: имя таблицы
        :param condition: элемент условия
        :return: элемент таблица
        """
        if isinstance(table, Select):
            table = Table(None, table.alias, table)
        if condition is None:
            condition =  table.__condition
        table1  = InnerJoin(table, condition)
        self.addTable(table1)
        table.alias = table1.alias
        return self

    def Join(self, table, condition = None):
        """
         добавить связанную таблицу
        :param table: имя таблицы
        :param condition: элемент условия
        :return: элемент таблица
        """
        if isinstance(table, Select):
            table = Table(None, table.alias, table)
        if condition is  None:
            condition =  table.__condition
        table1  = Join(table, condition)
        self.addTable(table1)
        table.alias = table1.alias
        return self

    def as_(self, alias = None, useSelect = None):
        return As(self,alias,useSelect)
    
    def OrderBy(self,*args, **kwargs):
        if isinstance(args,list):
            self._order_By = args  
        else:    
            self._order_By = list(args)
        return self
    def getOrderBy(self):
        return self._order_By
    def setOrderBy(self, oreder):
        self._order_By = oreder
    def Limit(self,limit):
        self.limit = limit
        return self

    def OffSet(self,offset):
        self.offset = offset
        return self 

    def GroupBy(self,*args, **kwargs):
        self._group_By = list(args)
        return self
   
    def find_type_object(self, type, comparator = None , setobject = None):
        self_where = self.getWhere()
        self_tab = self.getTables()
        alias_table = Select.getNameAndAlias(self_tab)
        ret = []
        
        return self_where.find_type_object( type, comparator , setobject)
                
    @staticmethod
    def processTables(table):
        if isinstance(table, Select) and True == table.useSelect: return ' (%s) %s' % (table,table.alias)
        if isinstance(table, Select): return '"%s"' % table.alias
        ##TODO сделать для выборки как талицы
        #if isinstance(table, Select): return '(%s) "%s"' % (table ,table.alias)
        return str(table)

    def __str__(self):
        self.outSql = ''
        def converTableToColumn(element):
            if isinstance(element,Table):
                return str(Column(element, '*'))
            else:
                return str(element)
            
        def reuseOrdGrLimOfset(obj):
            if obj._order_By:
                obj.outSql += ''' ORDER BY \n'''
                obj.outSql += ','.join(map(str,self._order_By))
                obj.outSql += '\n'    
            if obj._group_By:
                obj.outSql += ''' GROUP BY \n'''
                obj.outSql += ','.join(map(str,obj._group_By))
                obj.outSql += '\n'            
            if self.limit:
                obj.outSql += ' LIMIT (%s) \n' % obj.limit                
            if self.offset:
                obj.outSql += ' OFFSET (%s) \n' % obj.offset 
                            
        if self._columns :
            self.outSql += ''' SELECT \n'''
            self.outSql += ','.join(map(converTableToColumn,self._columns))
            self.outSql += '\n'
        if self._collectionTable:
            self.outSql += ''' FROM \n'''
            self.outSql += '\n'.join(map(self.processTables, self._collectionTable.values()))
            self.outSql += '\n'
        if self._where:
            self.outSql += ''' WHERE \n'''
            self.outSql += str(self._where)
            self.outSql += '\n'            
        
        ##reuseOrdGrLimOfset(self) 
          
        if (self.unions and self.unionsAll) :
            self.outSql += ''' UNION ALL\n'''
            self.outSql += ''' UNION ALL\n '''.join(map(str,self.unions))
            self.outSql += '\n' 
            reuseOrdGrLimOfset(self)
        elif (self.unions and self.unionsAll is False):  
            self.outSql = '(' + self.outSql + ')'  
            self.outSql += ''' UNION (\n'''
            self.outSql += ''') UNION (\n '''.join(map(str,self.unions))
            self.outSql += ')\n'
        
        reuseOrdGrLimOfset(self)     
            
            
            
            

        
               
        return  self.outSql

class With(Select):
   """
   класс конструкции WITH
   """ 
   _collectionSelect = OrderedDict()

   def __init__(self, *args, **kwargs ):
       self._collectionSelect =  list(args)
   
   def __getattr__(self, select):
        if isinstance(select,Select) :
            select.rev = True
        return  select
       
   def addSelect(self, alias, select):
       self._collectionSelect[alias] = select

   def generateAlias(self):
        """
        генератор псевдонима таблицы
        :param nameTable: имя таблицы
        :return:
        """
        alias = 'A' + str(len(self._collectionSelect))
        return alias

   def getSelect(self):
       return self._collectionSelect

   def getSelectByAlias(self,alias):
       return self._collectionSelect[alias]

   def Select(self, *args, **kwargs):
        self._columns = None
        self._where = None
        self._collectionTable = OrderedDict()
        self.unions = []
        self._order_By = None
        self._group_By = None
        self.limit = None
        self.offset = None
        
        self._columns =  list(args)
        self._tables = None
        self.alias = None
        self.rev = False
        self.useSelect = None
        self.unionsAll = False
        return self

   def __str__(self):
        self.outSql = " WITH  "
        self.outSql += '\n'
        if self._collectionSelect :
            self.outSql += ' ,\n '.join(map(str, self._collectionSelect))
        self.outSql +='\n' + super(With, self).__str__()
        return  self.outSql

class RecFunction(Table):
    """
    Класс функции рекурсивного запроса
    """
    def __init__(self, name):
        super(RecFunction, self).__init__(None, name)
        self.arguments = []

    def __getattr__(self, attr):
        argument = FuncArg(self, attr)
        self.addArgument(argument )
        return argument
    
    def addArgument(self,argument):
        arguments = self.getArguments()
        isExist = False
        for ar in  arguments:
            if ar.name == argument.name:
                isExist = True
        if not isExist:
           self.arguments.append(argument)    
        
    def getArguments(self):
        return self.arguments

    def __str__(self):
        self.outSql = self.alias
        return  self.outSql

class With_Recursive(Select):
    """
    Класс Рекурсивного запроса
    """
    def __init__(self, function):
        self.function = function
        self.select = None

    def As(self,select):
          self.select = select
          return self

    def getSelect(self):
        return self.select

    def getFunction(self):
            return self.function

    def Select(self, *args, **kwargs):
        self._columns = None
        self._where = None
        self._collectionTable = OrderedDict()
        self._order_By = None
        self._group_By = None
        self.unions = []
        self._columns =  list(args)
        self._tables = None
        self.alias = None
        self.limit = None
        self.offset = None
        self.unionsAll = False
        return self

    def __str__(self):
          self.outSql = " WITH RECURSIVE "
          self.outSql +=  str( self.function )
          def getArg(col):
              return str(col.name)
          if  len(self.function.arguments)>0:
              self.outSql += '(' + ', '.join(map(getArg, self.function.arguments)) + ')'
          if self.select:
              self.outSql += " AS (" + str( self.select ) + ")"
          if isinstance(self._columns, (list)):    
              self.outSql +='\n' + super(With_Recursive, self).__str__()
          return self.outSql

class SelectFrom(Expression):
     """
     класс для констркуции Select ()
     """
     def __init__(self, expression):
        self.expression = expression
     def __str__(self):
         return 'SELECT (%s)' % (self.expression )

class As(Expression):

    def __init__(self, expression, output_name, useSelect = None):
        self.expression = expression
        self.output_name = output_name
        self.useSelect = useSelect
        if isinstance(expression, (Column,Select)):
            expression.setAlias(output_name)

    def __str__(self):
        if isinstance(self.expression, (Column, Type, Coalesce, Case , Function)):
            return '%s AS "%s"' % (self.expression ,self.output_name)
        elif(isinstance(self.expression, (Select, With_Recursive)) and self.useSelect):            
            return '%s  %s' % (self.expression ,self.output_name)
        elif(isinstance(self.expression, (Select, OR ,AND)) and self.expression.rev ):
            return '(%s) AS "%s"' % (self.expression ,self.output_name)
        else:
            return '"%s" AS (%s)' % ( self.output_name,self.expression )
        
        