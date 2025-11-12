from typing import Literal

from parse.parsenode import *
from process.binding import Resolver, DeclarationSite
from codegen.block import Block
from codegen.consts import *
import codegen.writer as writer

class FunctionContext:
    local_slot_assignment = dict['DeclarationSite', tuple[int, Literal['local','cell']]]

class ModuleContext:
    global_slot_assignment = dict['DeclarationSite', int]

class Codegen():
    contexts: list[FunctionContext|ModuleContext]
    def __init__(self, resolver: Resolver):
        self.resolver = resolver
        self.contexts = []
        self.blocks = []

    # TODO: future optimization: do a first pass on non-function-literals in global scope to increase number of load_global instructions
    def compile_program(self, root: ProgramNode, resolver: Resolver):
        block = Block('module')
        module = ModuleContext()

        self.blocks = [block]
        self.contexts = [module]

        for statement in root.statements:
            self._generate_bytecode(statement)
        return block
    
    def _generate_bytecode(self, node: Node):
        context = self.contexts[-1]
        block = self.blocks[-1]

        match node:
            case ProgramNode():
                raise NotImplementedError("Not implemented for ProgramNodes; please use compile_program")
            
            case BlockNode():
                for statement in node.statements[:-1]:
                    self._generate_bytecode(statement)
                
                if isinstance(context, FunctionContext):
                        if len(node.statements) > 0 and type(node.statements[-1]) is ExpressionStatementNode:
                            self._generate_bytecode(node.statements[-1].expr)
                            block.emit_return()
                        else:
                            if len(node.statements) > 0:
                                self._generate_bytecode(node.statements[-1])
                            idx = block.get_const_index(NoneConst())
                            block.emit_load_const(idx)             
                            block.emit_return()
                        

            case NumberLiteralExpressionNode():
                idx = block.get_const_index(IntegerConst(node.number.token.content))
                block.emit_load_const(idx)

            case StringLiteralExpressionNode():
                idx = block.get_const_index(StringConst(node.string.token.content))
                block.emit_load_const(idx)

            # case NoneLiteralNode():
            #     idx = block.get_const_index(NoneConst())
            #     block.emit_load_const(idx)
            
            case BoolLiteralExpressionNode():
                idx = block.get_const_index(BoolConst(1 if node.bool.get_value() else 0))
                block.emit_load_const(idx)

            case ObjectLiteralExpressionNode():
                block.emit_make_object()

                for entry in node.contents:
                    self._generate_bytecode(entry)

                # if node.modifier == "frozen":
                #     block.emit_freeze()
                # elif node.modifier == "sealed":
                #     block.emit_seal()

            case ObjectLiteralEntryNode():
                self._generate_bytecode(node.name)
                self._generate_bytecode(node.value)
                block.emit_store_attr()

            case IdentifierExpressionNode():
                # if we're at a module level:
                # - always use LOAD_NAME
                # if we're at a function level:
                # - check if it's a cell/free var
                # - then check if it's a local var
                # - otherwise load name
                # TODO: load from global names
                if context == 'module':
                    idx = block.get_insert_name_index(node.identifier.token.content)
                    block.emit_load_name(idx)

                elif context == "function" or context == "expression":
                    if (idx := block.get_deref_index(node.identifier.token.content)) != None:
                        block.emit_load_deref(idx)
                    elif (idx := block.get_local_index(node.identifier.token.content)) != None:
                        block.emit_load_local(idx)
                    else:
                        idx = block.get_insert_name_index(node.identifier.token.content)
                        block.emit_load_name(idx)

                else:
                    raise Exception(f"Not implemented for context {context}")

            case LetStatementNode():
                left = node.name
                
                if context == "function":
                    self._generate_bytecode(node.value)
                    if (idx := block.get_deref_index(left.token.content)) != None:
                        block.emit_store_deref(idx)
                    else:
                        if (block.get_local_index(left.token.content)) != None:
                            raise Exception("duplicate binding")
                        idx = block.get_insert_local_index(left.token.content)
                        block.emit_store_local(idx)
                
                elif context == "module":
                    self._generate_bytecode(node.value)
                    idx = block.get_insert_name_index(left.token.content)
                    block.emit_store_name(idx)

            case IfElseExpressionNode():
                conditions = []
                condition_jumps = []
                end_jumps = []

                has_else = False

                for i, (cond, body) in enumerate(node.cases):
                    if cond is None:
                        # else case
                        if i != len(node.cases) - 1:
                            raise Exception("Encountered else block before end of IfThenExpression")
                        if has_else:
                            raise Exception("Encountered multiple else blocks")
                        has_else = True
                        self._generate_bytecode(body)
                        break
                    else:
                        if has_else:
                            raise Exception("Encountered condition after else")
                        
                        conditions.append(len(block.body))
                        self._generate_bytecode(cond)
                        block.emit_jump_forward_false(0)

                        # -2 to position at start of jump address (16 bits)
                        condition_jumps.append(len(block.body) - 2)
                        self._generate_bytecode(cond)

                        # we don't need an end jump if this is the last condition
                        if i != len(node.cases) - 1:
                            block.emit_jump_forward(0)
                            end_jumps.append(len(block.body) - 2)

                conditions.append(len(block.body))
                print("offsets:")
                print(conditions)
                print(condition_jumps)

                for i in range(len(condition_jumps)):
                    jump_location = condition_jumps[i]
                    # +1 since jump location is positioned at the start of the arg
                    # INSTR ARG0 ARG1
                    #       ^ jump_location
                    offset = conditions[i + 1] - jump_location + 1
                    writer.overwrite_int_as_uint16(block.body, offset, jump_location)

                for i in range(len(end_jumps)):
                    jump_location = end_jumps[i]
                    offset = conditions[-1] - jump_location + 1
                    writer.overwrite_int_as_uint16(block.body, offset, jump_location)

            case ExpressionStatementNode():
                expr = node.expr

                self._generate_bytecode(expr)
                block.emit_pop()

            case CallExpressionNode():
                self._generate_bytecode(node.callee)
                for arg in node.arglist.arguments:
                    self._generate_bytecode(arg.expr)
                block.emit_call(len(node.arglist.arguments))

            case BinaryExpressionNode():
                self._generate_bytecode(node.left)
                self._generate_bytecode(node.right)
                match node.operator:
                    case 'plus':
                        block.emit_add()
                    case 'minus':
                        block.emit_subtract()
                    case 'asterisk':
                        block.emit_multiply()
                    case 'slash':
                        block.emit_divide()
                    case 'and':
                        block.emit_and()
                    case 'or':
                        block.emit_or()
                    case 'greater':
                        block.emit_gt()
                    case 'greaterequals':
                        block.emit_gteq()
                    case 'less':
                        block.emit_lt()
                    case 'lessequals':
                        block.emit_lteq()
                    case 'equalsequals':
                        block.emit_eq()
                    case 'bangequals':
                        block.emit_neq()
                    case _:
                        raise NotImplementedError(f"Not implemented for binary operation {node.operator}")
                    
            case PrefixExpressionNode():
                match node.operator:
                    case 'minus':
                        generate_bytecode(node.operand, block, resolver, context)
                        block.emit_negate()
                    case 'plus':
                        generate_bytecode(node.operand, block, resolver, context)
                        block.emit_positive()

            case AssignmentExpressionNode():
                if context == "module":
                    idx = block.get_insert_name_index(node.left.identifier.token.content)
                    generate_bytecode(node.value, block, resolver, context)
                    block.emit_store_name(idx)
                    
                    # since assignment is an expression we always push None
                    none_idx = block.get_const_index(NoneConst())
                    block.emit_load_const(none_idx)

                if context == "function":
                    if (idx := block.get_deref_index(node.left.identifier.token.content)) != None:
                        block.emit_store_deref(idx)
                    elif (idx := block.get_local_index(node.left.identifier.token.content)) != None:
                        block.emit_store_local(idx)
                    else:
                        idx = block.get_insert_name_index(node.left.identifier.token.content)
                        block.emit_store_name(idx)

                else:
                    raise Exception(f"Not implemented for context {block.context}")
                
            # case ObjectAssignmentExpressionNode():
            #     generate_bytecode(node.left.object, block)
            #     generate_bytecode(node.left.index, block)
            #     generate_bytecode(node.right, block)
            #     block.emit_store_attr()

            #     # since assignment is an expression we always push None
            #     none_idx = block.get_const_index(NoneConst())
            #     block.emit_load_const(none_idx)

            case FunctionLiteralExpressionNode():
                function_block = Block(context='function')
                bound_names = set()

                for param in node.paramlist.parameters:
                    if param.name.token.content in bound_names:
                        raise Exception(f"Param {param.name.token.content} declared more than once!")
                    bound_names.add(param.name.token.content)
                    function_block.get_insert_local_index(param.name.token.content)

                free_vars = self.resolver.free_variables.get(node)
                if free_vars is not None:
                    for freevar in free_vars:
                        if freevar in bound_names:
                            raise Exception(f"Captured variable {freevar} conflicts with parameter of same name (should be impossible)")
                        bound_names.add(freevar)
                        function_block.free_names.append(freevar)
                    function_block.emit_copy_free_vars()

                cell_vars = self.resolver.cell_variables.get(node)
                if cell_vars is not None:
                    for cellvar in cell_vars:
                        if cellvar in bound_names:
                            raise Exception("Cell var conflicts with param or free var (should be unreachable)")
                        bound_names.add(cellvar)
                        function_block.cell_names.append(cellvar)

                ctx = FunctionContext()
                
                self._generate_bytecode(node.body)

                idx = block.get_const_index(FunctionLiteralConst(function_block))
                block.emit_load_const(idx)

            case IndexExpressionNode():
                self._generate_bytecode(node.left)
                self._generate_bytecode(node.index)
                block.emit_load_attr()

            case _:
                raise NotImplementedError(f"Not implemented for {type(node)}")