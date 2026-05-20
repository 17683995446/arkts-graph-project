
import re
from typing import List, Dict, Any
import database


class ArkTSClass:
    def __init__(self, name, is_component=False):
        self.name = name
        self.is_component = is_component
        self.methods = []
        self.calls = []
        self.child_components = []


class ArkTSAnalyzer:
    def __init__(self):
        self.classes = []
        self.current_class = None
    
    def analyze_file(self, file_path):
        self.classes = []
        self.current_class = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._extract_classes(content)
        return self.classes
    
    def _extract_classes(self, content):
        class_pattern = r'(?:@Component\s+)?(?:@Entry\s+)?struct\s+(\w+)|class\s+(\w+)'
        matches = list(re.finditer(class_pattern, content))
        
        for i, match in enumerate(matches):
            struct_name = match.group(1)
            class_name = match.group(2)
            name = struct_name or class_name
            
            is_component = struct_name is not None or '@Component' in content[max(0, match.start()-150):match.start()]
            
            class_obj = ArkTSClass(name, is_component)
            self.classes.append(class_obj)
            
            # 使用平衡括号算法
            start_pos = match.end()
            open_braces = 0
            in_string = False
            escape_next = False
            content_end = start_pos
            
            for idx, c in enumerate(content[start_pos:]):
                if escape_next:
                    escape_next = False
                elif c == '\\':
                    escape_next = True
                elif c in ('"', "'", '`'):
                    in_string = not in_string
                elif not in_string and c == '{':
                    open_braces += 1
                elif not in_string and c == '}':
                    open_braces -= 1
                    if open_braces == 0:
                        content_end = start_pos + idx + 1
                        break
            
            class_content = content[start_pos:content_end]
            
            self._extract_methods(class_content, class_obj)
            self._extract_calls(class_content, class_obj)
            
            if is_component:
                self._extract_child_components(class_content, class_obj)
    
    def _extract_methods(self, content, class_obj):
        method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*{'
        matches = re.finditer(method_pattern, content)
        for match in matches:
            method_name = match.group(1)
            if method_name not in ['if', 'for', 'while', 'switch', 'return', 'let', 'const', 'async', 'export', 'import', 'type', 'interface', 'function']:
                if method_name and len(method_name) > 0:
                    class_obj.methods.append(method_name)
    
    def _extract_calls(self, content, class_obj):
        # 关键改进！先获取方法名，再提取调用！
        method_set = set(class_obj.methods)
        call_pattern = r'(\w+)\s*\('
        matches = re.finditer(call_pattern, content)
        for match in matches:
            call_name = match.group(1)
            if call_name in ['if', 'for', 'while', 'switch', 'return', 'let', 'const', 'this', 'new', 'async', 'function']:
                continue
            if call_name in method_set:
                continue
            if call_name and len(call_name) > 0 and call_name not in class_obj.calls:
                class_obj.calls.append(call_name)
    
    def _extract_child_components(self, content, class_obj):
        current_methods = set(class_obj.methods)
        
        component_pattern = r'(?:<\s*(\w+)|(\w+)\s*\([^)]*\))'
        matches = re.finditer(component_pattern, content)
        for match in matches:
            component_name = match.group(1) or match.group(2)
            if component_name and len(component_name) > 0 and component_name not in class_obj.child_components:
                if not component_name[0].isupper():
                    continue
                if component_name in ['Text', 'Button', 'Column', 'Row', 'List', 'ListItem', 'ForEach']:
                    continue
                if component_name not in current_methods and component_name != class_obj.name:
                    class_obj.child_components.append(component_name)


def update_file_knowledge_graph(file_path):
    analyzer = ArkTSAnalyzer()
    classes = analyzer.analyze_file(file_path)
    file_hash = database.compute_file_hash(file_path)
    
    existing_file = database.get_file_by_path(file_path)
    if existing_file:
        database.delete_file_data(existing_file['id'])
    
    file_id = database.insert_file(file_path, file_hash)
    
    class_name_to_id = {}
    method_name_to_id = {}
    
    for cls in classes:
        flags = 0
        if cls.is_component:
            flags = 1
        
        class_id = database.insert_class(cls.name, file_id, flags)
        class_name_to_id[cls.name] = class_id
        
        for method_name in cls.methods:
            method_id = database.insert_method(method_name, class_id)
            method_name_to_id[f"{cls.name}.{method_name}"] = method_id
    
    for cls in classes:
        class_id = class_name_to_id[cls.name]
        
        if cls.is_component:
            for child_name in cls.child_components:
                if child_name in class_name_to_id:
                    child_id = class_name_to_id[child_name]
                    database.insert_component(class_id, child_id)
        
        for method_name in cls.methods:
            for called_name in cls.calls:
                if called_name in cls.methods:
                    caller_key = f"{cls.name}.{method_name}"
                    callee_key = f"{cls.name}.{called_name}"
                    if caller_key in method_name_to_id and callee_key in method_name_to_id:
                        caller_id = method_name_to_id[caller_key]
                        callee_id = method_name_to_id[callee_key]
                        database.insert_call(caller_id, callee_id)


def parse_file(file_path):
    analyzer = ArkTSAnalyzer()
    classes = analyzer.analyze_file(file_path)
    
    result = {"classes": []}
    for cls in classes:
        result["classes"].append({
            "name": cls.name,
            "is_component": cls.is_component,
            "methods": cls.methods,
            "calls": cls.calls,
            "child_components": cls.child_components
        })
    
    return result
