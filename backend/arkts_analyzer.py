
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
        # UI组件名称列表 - 这些不是类的方法
        ui_components = {
            'Text', 'Button', 'Column', 'Row', 'Stack', 'List', 'ListItem',
            'Image', 'Scroll', 'ForEach', 'If', 'LazyForEach', 'Repeat',
            'Navigation', 'NavDestination', 'Tabs', 'TabBar', 'TabContent',
            'Grid', 'GridItem', 'Swiper', 'Navigator', 'Search', 'TextInput',
            'TextArea', 'Checkbox', 'Radio', 'Switch', 'Slider', 'Progress',
            'LoadingProgress', 'Blank', 'Divider', 'Badge', 'QrCode',
            'AlphabetIndexer', 'Gesture', 'TouchGesture', 'PanGesture',
            'PinchGesture', 'RotationGesture', 'LongPressGesture',
            'Animation', 'Animator', 'Transition', 'Environment'
        }
        
        method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*{'
        matches = re.finditer(method_pattern, content)
        for match in matches:
            method_name = match.group(1)
            # 排除关键字
            if method_name in ['if', 'for', 'while', 'switch', 'return', 'let', 'const', 'async', 'export', 'import', 'type', 'interface', 'function']:
                continue
            # 排除UI组件
            if method_name in ui_components:
                continue
            # 排除私有变量（可能有getter/setter）
            if method_name.startswith('_'):
                continue
            if method_name and len(method_name) > 0:
                class_obj.methods.append(method_name)
    
    def _extract_calls(self, content, class_obj):
        # UI组件名称列表 - 这些不是方法的调用
        ui_components = {
            'Text', 'Button', 'Column', 'Row', 'Stack', 'List', 'ListItem',
            'Image', 'Scroll', 'ForEach', 'If', 'LazyForEach', 'Repeat',
            'Navigation', 'NavDestination', 'Tabs', 'TabBar', 'TabContent',
            'Grid', 'GridItem', 'Swiper', 'Navigator', 'Search', 'TextInput',
            'TextArea', 'Checkbox', 'Radio', 'Switch', 'Slider', 'Progress',
            'LoadingProgress', 'Blank', 'Divider', 'Badge', 'QrCode',
            'AlphabetIndexer', 'Gesture', 'TouchGesture', 'PanGesture',
            'PinchGesture', 'RotationGesture', 'LongPressGesture',
            'Animation', 'Animator', 'Transition', 'Environment'
        }
        
        # 关键字列表 - 这些不是方法调用
        keywords = {
            'if', 'for', 'while', 'switch', 'return', 'let', 'const',
            'this', 'new', 'async', 'function', 'class', 'interface',
            'type', 'enum', 'import', 'export', 'from', 'default',
            'try', 'catch', 'finally', 'throw', 'break', 'continue',
            'console', 'log', 'debug', 'warn', 'error', 'info'
        }
        
        # 提取所有函数调用模式
        # 1. this.xxx() 形式
        this_call_pattern = r'this\.(\w+)\s*\('
        matches = re.finditer(this_call_pattern, content)
        for match in matches:
            call_name = match.group(1)
            if call_name not in class_obj.calls:
                class_obj.calls.append(call_name)
        
        # 2. 直接 xxx() 形式
        direct_call_pattern = r'(\w+)\s*\('
        matches = re.finditer(direct_call_pattern, content)
        for match in matches:
            call_name = match.group(1)
            # 排除关键字
            if call_name in keywords:
                continue
            # 排除UI组件
            if call_name in ui_components:
                continue
            # 排除自身方法（已通过this.xxx()处理）
            if call_name in class_obj.methods:
                continue
            # 排除已经添加的
            if call_name in class_obj.calls:
                continue
            # 添加其他方法调用
            if call_name and len(call_name) > 0:
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
    # 优化：先检查文件是否存在，计算 hash
    if not file_path or not isinstance(file_path, str):
        return
        
    if not __import__('os').path.exists(file_path):
        return
    
    file_hash = database.compute_file_hash(file_path)
    
    # 检查文件是否已经存在且 hash 没有变更
    existing_file = database.get_file_by_path(file_path)
    if existing_file:
        # 比较 hash（注意处理类型问题）
        existing_hash = existing_file['hash']
        if isinstance(existing_hash, (bytes, bytearray)):
            existing_hash = existing_hash.hex()
        
        if existing_hash == file_hash:
            # 文件没有变更，跳过
            return
        
        # 文件变更了，删除旧数据
        database.delete_file_data(existing_file['id'])
    
    # 现在进行分析
    analyzer = ArkTSAnalyzer()
    classes = analyzer.analyze_file(file_path)
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
        
        # 创建方法间的调用关系
        for method_name in cls.methods:
            for called_name in cls.calls:
                # 检查被调用的方法是否在当前类中
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
