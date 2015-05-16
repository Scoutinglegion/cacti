from cacti.runtime import *
from cacti.exceptions import *

__all__ = ['ClassDefinition', 'Closure', 'Function', 'Method', 'MethodDefinition', 'ObjectDefinition', 'PropertyDefinition', 'TypeDefinition']
           

# All ObjectDefinition Instances Have This
class ObjectDefinition:
    def __init__(self, superobj, *, typeobj=None, name=''):
        self.__typeobj = typeobj
        self.__name = name
        self.__selfobj = self
        self.__superobj = superobj
        
        self.__internal_table = SymbolTable()
        
        if self.__superobj:
            self.__superobj.set_selfobj(self)
        
        self.__field_table = SymbolTable()
        
        parent_hook_table = superobj.hook_table if superobj else None
        self.__hook_table = SymbolTable(parent_table=parent_hook_table, symbol_validator=isvalidhook)
        
        parent_property_table = superobj.property_table if superobj else None
        self.__property_table = SymbolTable(parent_table=parent_property_table)
        
        self.__public_table = self.__property_table
        self.__private_table = SymbolTableChain(self.__property_table, self.__field_table)
        
    @property
    def internal_table(self):
        return self.__internal_table
        
    def set_typeobj(self, typeobj):
        self.__typeobj = typeobj
        
    def set_selfobj(self, selfobj):
        self.__selfobj = selfobj
    
    @property
    def public_table(self):
        return self.__public_table
        
    @property
    def private_table(self):
        return self.__private_table
        
    @property
    def hook_table(self):
        return self.__hook_table
        
    @property
    def property_table(self):
        return self.__property_table
        
    @property
    def selfobj(self):
        return self.__selfobj
    
    @property
    def superobj(self):
        return self.__superobj
        
    @property
    def typeobj(self):
        return self.__typeobj
        
    @property
    def name(self):
        return self.__name
        
    def add_hook(self, hook_name, hook_callable):
        binding = MethodBinding(self, hook_name, hook_callable)
        self.__hook_table.add_symbol(hook_name, ConstantValueHolder(binding))
    
    def add_val(self, val_name, val_value):
        self.__field_table.add_symbol(val_name, ConstantValueHolder(val_value))
    
    def add_var(self, var_name, var_value):
        self.__field_table.add_symbol(var_name, ValueHolder(var_value))
        
    def add_method(self, method_name, method_callable):
        method = Method(self, method_name, method_callable)
        const_value = ConstantValueHolder(method)
        self.__property_table.add_symbol(method_name, const_value)
        
    def add_property(self, property_name, get_callable, set_callable):
        value_holder = None
        
        if get_callable is None and set_callable is None:
            value_holder = ValueHolder()
        elif get_callable is not None and set_callable is not None:
            value_holder = PropertyGetValueHolder(
                MethodBinding(self, property_name, get_callable))
        elif get_callable is not None and set_callable is None:
            value_holder = PropertyGetSetValueHolder(
                MethodBinding(self, property_name, get_callable),
                MethodBinding(self, property_name, set_callable))
        else:
            raise Exception('TBD')
        
        self.__property_table.add_symbol(property_name, value_holder)
        
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return self.to_string()
    
    # This is a workaround to the fact that
    # str() will not call the __str__() that
    # is dynamically added to an object instance
    def to_string(self):
        return '{}<{}>'.format(self.typeobj.name, id(self))

class PrimitiveObjectDefinition(ObjectDefinition):
    def __init__(self, superobj, *, typeobj=None, name=''):
        super().__init__(superobj, typeobj=typeobj, name=name)

class Closure(ObjectDefinition):
    def __init__(self, closure_call_env, closure_callable):
        from cacti.builtin import get_builtin, get_type
        binding = ClosureBinding(closure_call_env, closure_callable)
        superobj = get_builtin('Object').hook_table['()'].call()
        super().__init__(superobj, typeobj=get_type('Closure'))
        self.add_hook('()', binding)
        
class Function(ObjectDefinition):
    def __init__(self, function_name, function_callable):
        from cacti.builtin import get_builtin, get_type
        binding = FunctionBinding(self, function_name, function_callable)
        superobj = get_builtin('Object').hook_table['()'].call()
        super().__init__(superobj, typeobj=get_type('Function'), name=function_name)
        self.add_hook('()', binding)
        
    def __str__(self):
        return "Function<'{}'>".format(self.name)
        
class Method(ObjectDefinition):
    def __init__(self, method_owner, method_name, method_callable):
        from cacti.builtin import get_builtin, get_type
        binding = MethodBinding(method_owner, method_name, method_callable)
        superobj = get_builtin('Object').hook_table['()'].call()
        super().__init__(superobj, typeobj=get_type('Method'), name=method_name)
        self.add_hook('()', binding)
        
    def __str__(self):
        return "Method<'{}'>".format(self.name)
        
class TypeDefinition(ObjectDefinition):
    def __init__(self, superobj, name, *, typeobj=None):
        super().__init__(superobj, typeobj=typeobj, name=name)
        self.add_property(
            'name',
            Callable(lambda: peek_call_env().symbol_stack['self'].name),
            None)
    
    def __str__(self):
        return '{}<{}>'.format('Type', self.name)
        
class ClassDefinition(TypeDefinition):
    def __init__(self, superobj, name, *, typeobj=None, superclass=None):
        super().__init__(superobj, typeobj=typeobj, name=name)
        self.__superclass = superclass
        self.__hook_defs = []
        self.__val_defs = []
        self.__var_defs = []
        self.__method_defs = []
        self.__property_defs = []
        
    def set_superclass(self, superclass):
        self.__superclass = superclass
        
    @property
    def superclass(self):
        return self.__superclass
        
    @property
    def hook_definitions(self):
        return self.__hook_defs
        
    @property
    def val_definitions(self):
        return self.__val_defs
        
    @property
    def var_definitions(self):
        return self.__var_defs
        
    @property
    def method_definitions(self):
        return self.__method_defs
        
    @property
    def property_definitions(self):
        return self.__property_defs
        
    def add_hook_definition(self, hook_def):
        self.__hook_defs += [hook_def]
        
    def add_val_definition(self, val_def):
        self.__val_defs += [val_def]
        
    def add_var_definition(self, var_def):
        self.__var_def += [var_def]
        
    def add_method_definition(self, method_def):
        self.__method_defs += [method_def]
        
    def add_property_definition(self, prop_def):
        self.__property_defs += [prop_def]
        
    def __str__(self):
        return '{}<{}>'.format('Class', self.name)

class MethodDefinition:
    def __init__(self, method_name, method_callable):
        self.__method_name = method_name
        self.__method_callable = method_callable
        
    @property
    def name(self):
        return self.__method_name
        
    @property
    def callable(self):
        return self.__method_callable
        
class PropertyDefinition:
    def __init__(self, property_name, *, getter_callable=None, setter_callable=None):
        self.__property_name = property_name
        self.__getter_callable = getter_callable
        self.__setter_callable = setter_callable
        
    @property
    def name(self):
        return self.__property_name
        
    @property
    def getter_callable(self):
        return self.__getter_callable
        
    @property
    def setter_callable(self):
        return self.__setter_callable
        
class ValDefinition:
    def __init__(self, val_name, val_init_expr):
        self.__val_name = val_name
        self.__val_init_expr = val_init_expr
        
    @property
    def name(self):
        return self.__val_name
        
    @property
    def init_expr(self):
        return self.__val_init_expr

# class Callable(ObjectDefinition):
#     def check_arity(self, caller, *called_params):
#         if self.arity != len(called_params):
#             kwargs = {'caller': caller.type.name, 'method_name': self.__name, 'exp': self.arity, 'got': len(called_params)}
#             raise SyntaxError("{caller}.{method_name}: Expected {exp} parameter(s) but received {got}".format(**kwargs))
#     
