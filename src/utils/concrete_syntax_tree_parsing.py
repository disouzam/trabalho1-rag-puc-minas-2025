import libcst as cst


class TypingCollector(cst.CSTVisitor):
    def __init__(self):
        pass


class RemoveDocStringTransformer(cst.CSTTransformer):
    def __init__(self, visitor):
        self.visitor = visitor
        self.docstring: str | None = None

    def leave_Comment(self, original_node, updated_node):
        """Remove comments"""
        updated_node = cst.RemoveFromParent()
        return super().leave_Comment(original_node, updated_node)

    def leave_EmptyLine_comment(self, node):
        """Remove comments"""
        node = cst.RemoveFromParent()
        return super().leave_EmptyLine_comment(node)

    def leave_Element(self, original_node, updated_node):
        if isinstance(original_node, cst.EmptyLine):
            print(original_node)
        return super().leave_Element(original_node, updated_node)

    def visit_FunctionDef(self, node):
        docstring = node.get_docstring()
        if docstring is not None:
            self.docstring = docstring

    def visit_Module(self, node):
        docstring = node.get_docstring()
        if docstring is not None:
            self.docstring = docstring

    def leave_EmptyLine(self, original_node, updated_node):
        """Remove empty lines"""
        updated_node = cst.RemoveFromParent()
        return super().leave_EmptyLine(original_node, updated_node)

    def leave_SimpleString(self, original_node, updated_node):

        if original_node.value == f'"""{self.docstring}"""':
            new_node = cst.Comment("# It was a docstring before")
        else:
            new_node = updated_node

        return super().leave_SimpleString(original_node, new_node)

    def leave_Expr(self, original_node, updated_node):
        new_node = updated_node

        if self.docstring is not None:
            if isinstance(original_node.value, cst.SimpleString):

                docstring = self.docstring
                valueInExpr = original_node.value.value

                docstring = docstring.replace('"', " ")
                docstring = docstring.strip()
                docstring = docstring.split("\n")

                valueInExpr = valueInExpr.replace('"', " ")
                valueInExpr = valueInExpr.strip()
                valueInExpr = valueInExpr.split("\n")

                new_docstringList = []
                for entry in docstring:
                    if entry != "":
                        entry = entry.strip()
                        new_docstringList.append(entry)

                new_valueInExprList = []
                for entry in valueInExpr:
                    if entry != "":
                        entry = entry.strip()
                        new_valueInExprList.append(entry)

                docstring = ",".join(new_docstringList)
                valueInExpr = ",".join(new_valueInExprList)

                new_node = cst.RemoveFromParent()

        return super().leave_Expr(original_node, new_node)


class FunctionWithDocsStrings(cst.CSTVisitor):
    def __init__(self):
        pass


class RemoveFunctionsWithoutDocStrings(cst.CSTTransformer):
    def __init__(self, visitor):
        self.visitor = visitor
        self.function_chunks = []

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> (
        cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel
    ):
        docstring = original_node.get_docstring()

        if docstring is None or len(docstring.strip()) == 0:
            updated_node = cst.RemoveFromParent()
        else:
            # https://stackoverflow.com/questions/60867937/libcst-converting-arbitrary-nodes-to-code/63421188#63421188
            self.function_chunks.append(cst.Module([]).code_for_node(original_node))

        return super().leave_FunctionDef(original_node, updated_node)

    def leave_Arg(
        self, original_node: cst.Arg, updated_node: cst.Arg
    ) -> cst.Arg | cst.FlattenSentinel[cst.Arg] | cst.RemovalSentinel:
        return super().leave_Arg(original_node, updated_node)
