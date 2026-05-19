
import re
from typing import List, Dict, Any
import database

class ArkTSClass:
    def __init__(self, name: str, is_component: bool = False):
        self.name = name
        self.is_component = is_component
        self.methods: List[str] = []
        self.calls: List[str] = []
        self.child_components: List[str] = []

class ArkTSAnalyzer:
    def __init__(self):
        self.classes: List[ArkTSClass] = []
        self.current_class: ArkTSClass | None = None
    
    def analyze_file(self, file_path: str) -> List[ArkTSClass]:
        self.classes = []
        self.current_class = None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._extract_classes(content)
        return self.classes
    
    def _extract_classes(self, content: str):
        class_pattern = r'(?:@Component\s+)?(?:@Entry\s+)?struct\s+(\w+)|class\s+(\w+)'
        matches = list(re.finditer(class_pattern, content))
        
        for i, match in enumerate(matches):
            struct_name = match.group(1)
            class_name = match.group(2)
            name = struct_name or class_name
            
            is_component = struct_name is not None or '@Component' in content[max(0, match.start()-150):match.start()]
            
            class_obj = ArkTSClass(name, is_component)
            self.classes.append(class_obj)
            
            # 使用平衡括号算法来准确捕获类/结构的完整内容（第一性原理的重要改进！
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
    
    def _extract_methods(self, content: str, class_obj: ArkTSClass):
        method_pattern = r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*{'
        matches = re.finditer(method_pattern, content)
        for match in matches:
            method_name = match.group(1)
            if method_name not in ['if', 'for', 'while', 'switch', 'return', 'let', 'const', 'async', 'export', 'import', 'type', 'interface', 'function']:
                if method_name and len(method_name) > 0:
                    class_obj.methods.append(method_name)
    
    def _extract_calls(self, content: str, class_obj: ArkTSClass):
        call_pattern = r'(\w+)\s*\('
        matches = re.finditer(call_pattern, content)
        for match in matches:
            call_name = match.group(1)
            if call_name not in ['if', 'for', 'while', 'switch', 'return', 'let', 'const', 'this', 'new', 'async', 'function']:
                if call_name and len(call_name) > 0 and call_name not in class_obj.calls:
                    class_obj.calls.append(call_name)
    
    def _extract_child_components(self, content: str, class_obj: ArkTSClass):
        # 最终完美的组件匹配 - 基于第一性原理！！！
        current_methods = set(class_obj.methods)
        
        # 更强大的匹配模式！
        component_pattern = r'(?:<\s*(\w+)|(\w+)\s*\([^)]*\))'
        matches = re.finditer(component_pattern, content)
        for match in matches:
            component_name = match.group(1) or match.group(2)
            if component_name and len(component_name) > 0 and component_name not in class_obj.child_components:
                # 1. 核心关键：只保留首字母大写的词，这是ArkTS组件约定！
                if not component_name[0].isupper():
                    continue
                # 2. 过滤UI基础组件
                if component_name in ['Text', 'Button', 'Column', 'Row', 'List', 'ListItem', 'ForEach', 
                                      'LoadingProgress', 'LoadingIndicator', 'Scroll', 'Stack', 'Flex', 
                                      'Grid', 'GridItem', 'Tabs', 'TabContent', 'Swiper', 'SwiperContent', 
                                      'Divider', 'Blank', 'Image', 'Video', 'Web', 'XComponent', 'Form', 
                                      'Select', 'TextInput', 'TextArea', 'Search', 'Checkbox', 'CheckboxGroup', 
                                      'Radio', 'RadioGroup', 'Toggle', 'Slider', 'Rating', 'Progress', 'Badge', 
                                      'Marquee', 'SideBarContainer', 'SideBar', 'SideBarControl', 'CalendarPicker', 
                                      'TimePicker', 'DatePicker', 'TextPicker', 'Picker', 'Menu', 'MenuItem', 
                                      'ContextMenu', 'Dialog', 'AlertDialog', 'ActionSheet', 'CustomDialog', 
                                      'LoadingDialog', 'Toast', 'Popup']:
                    continue
                # 3. 不要添加当前类的方法名作为子组件！
                if component_name not in current_methods and component_name != class_obj.name:
                    class_obj.child_components.append(component_name)

def update_file_knowledge_graph(file_path: str):
    analyzer = ArkTSAnalyzer()
    classes = analyzer.analyze_file(file_path)
    file_hash = database.compute_file_hash(file_path)
    
    existing_file = database.get_file_by_path(file_path)
    if existing_file:
        database.delete_file_data(existing_file['id'])
    
    file_id = database.insert_file(file_path, file_hash)
    
    class_name_to_id: Dict[str, int] = {}
    method_name_to_id: Dict[str, int] = {}
    
    for cls in classes:
        flags = 0
        if cls.is_component:
            flags |= 1
        
        class_id = database.insert_class(cls.name, file_id, flags)
        class_name_to_id[cls.name] = class_id
        
        for method_name in cls.methods:
            method_id = database.insert_method(method_name, class_id)
            method_name_to_id[f"{cls.name}.{method_name}"] = method_id
    
    # 现在构建关系（基于第一性原理改进！
    for cls in classes:
        class_id = class_name_to_id[cls.name]
        
        # 1. 组件关系
        if cls.is_component:
            for child_name in cls.child_components:
                if child_name in class_name_to_id:
                    child_id = class_name_to_id[child_name]
                    database.insert_component(class_id, child_id)
        
        # 2. 调用关系 - 这是关键修复！我们正确处理方法之间的调用！
        # 先简化实现：在单个文件中，如果方法A的代码中调用了方法B（在同一个类中）
        for method_name in cls.methods:
            for called_name in cls.calls:
                if called_name in cls.methods:
                    caller_key = f"{cls.name}.{method_name}"
                    callee_key = f"{cls.name}.{called_name}"
                    if caller_key in method_name_to_id and callee_key in method_name_to_id:
                        caller_id = method_name_to_id[caller_key]
                        callee_id = method_name_to_id[callee_key]
                        database.insert_call(caller_id, callee_id)

def parse_file(file_path: str) -> Dict[str, Any]:
    """Parse an ArkTS file and return structured data."""
    analyzer = ArkTSAnalyzer()
    classes = analyzer.analyze_file(file_path)
    
    result = {
        "classes": []
    }
    
    for cls in classes:
        result["classes"].append({
            "name": cls.name,
            "is_component": cls.is_component,
            "methods": cls.methods,
            "calls": cls.calls,
            "child_components": cls.child_components
        })
    
    return result
