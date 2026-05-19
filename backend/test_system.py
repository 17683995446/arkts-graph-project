
#!/usr/bin/env python3
"""
Test script to validate core components of the ArkTS Knowledge Graph system
"""
import os
import sys
import tempfile
import shutil
import hashlib

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("  ArkTS Knowledge Graph - System Test Suite")
print("=" * 60)


def test_database():
    """Test database functionality"""
    print("\n[1/6] Testing database module...")
    try:
        import database
        
        # Initialize test database
        database.init_database()
        
        # Check database file exists
        if os.path.exists(database.DATABASE_PATH):
            print("   ✓ Database initialized successfully")
        else:
            print("   ✗ Database file not created")
            return False
        
        # Test insert a file
        test_file_path = "/test/path/file.ets"
        test_hash = b"test_hash"
        
        file_id = database.insert_file(test_file_path, test_hash)
        print(f"   ✓ File inserted with id: {file_id}")
        
        # Test retrieve the file
        file = database.get_file_by_path(test_file_path)
        if file and file['path'] == test_file_path:
            print("   ✓ File retrieved successfully")
        else:
            print("   ✗ Failed to retrieve inserted file")
            return False
        
        # Test insert class
        class_id = database.insert_class("TestComponent", file_id, 1)
        print(f"   ✓ Class inserted with id: {class_id}")
        
        # Test insert method
        method_id = database.insert_method("build", class_id)
        print(f"   ✓ Method inserted with id: {method_id}")
        
        # Test retrieve all files
        files = database.get_all_files()
        print(f"   ✓ Retrieved {len(files)} files from database")
        
        # Cleanup test database
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)
        
        return True
    except Exception as e:
        print(f"   ✗ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arkts_analyzer():
    """Test ArkTS analyzer functionality"""
    print("\n[2/6] Testing ArkTS analyzer module...")
    try:
        import arkts_analyzer
        
        # Create test directory and files
        test_dir = tempfile.mkdtemp()
        
        test_file_content = """@Entry
@Component
struct Index {
    @State message: string = "Hello"
    
    build() {
        Column() {
            Text(this.message)
            ChildComponent()
        }
    }
    
    doSomething() {
        console.log("test")
    }
}

@Component
struct ChildComponent {
    build() {
        Text("Child")
    }
}
"""
        
        test_file_path = os.path.join(test_dir, "TestFile.ets")
        with open(test_file_path, "w") as f:
            f.write(test_file_content)
        
        # Test analyzer
        analyzer = arkts_analyzer.ArkTSAnalyzer()
        classes = analyzer.analyze_file(test_file_path)
        
        if classes:
            print(f"   ✓ Found {len(classes)} classes/structs in test file")
            for cls in classes:
                print(f"     - {cls.name} (component: {cls.is_component})")
                if cls.methods:
                    print(f"       Methods: {', '.join(cls.methods)}")
        else:
            print("   ✗ No classes found in test file")
            shutil.rmtree(test_dir)
            return False
        
        # Cleanup
        shutil.rmtree(test_dir)
        return True
    except Exception as e:
        print(f"   ✗ ArkTS analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_file_monitor():
    """Test file monitor basic functionality"""
    print("\n[3/6] Testing file monitor module...")
    try:
        import file_monitor
        
        # Just test we can import and create the objects
        queue = file_monitor.ChangeQueue()
        print("   ✓ ChangeQueue object created successfully")
        
        monitor = file_monitor.FileMonitorService("/tmp", 1000)
        print("   ✓ FileMonitorService object created successfully")
        
        return True
    except Exception as e:
        print(f"   ✗ File monitor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_handler():
    """Test LLM handler (without actually calling external API)"""
    print("\n[4/6] Testing LLM handler module...")
    try:
        import llm_handler
        
        # Just test module import and class instantiation
        handler = llm_handler.LLMQueryHandler()
        print("   ✓ LLMQueryHandler object created successfully")
        
        return True
    except Exception as e:
        print(f"   ✗ LLM handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints():
    """Test API definitions and basic types"""
    print("\n[5/6] Testing API structure...")
    try:
        import main
        from fastapi.testclient import TestClient
        
        # Check that the FastAPI app is created successfully
        print(f"   ✓ FastAPI app initialized with title: {main.app.title}")
        
        return True
    except Exception as e:
        print(f"   ✗ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_workflow():
    """Test the full end-to-end workflow"""
    print("\n[6/6] Testing end-to-end workflow...")
    try:
        import database
        import arkts_analyzer
        
        # Create test directory and files
        test_dir = tempfile.mkdtemp()
        test_project_dir = os.path.join(test_dir, "example")
        os.makedirs(test_project_dir)
        
        # Create some test files
        test_file_content1 = """@Entry
@Component
struct Index {
    build() {
        Column() {
            Text("Hello")
        }
    }
}
"""
        test_file_content2 = """@Component
struct MyButton {
    build() {
        Button("Click Me")
    }
}
"""
        
        with open(os.path.join(test_project_dir, "Index.ets"), "w") as f:
            f.write(test_file_content1)
        with open(os.path.join(test_project_dir, "MyButton.ets"), "w") as f:
            f.write(test_file_content2)
        
        # Initialize database
        database.init_database()
        
        # Process files
        for filename in os.listdir(test_project_dir):
            if filename.endswith(".ets"):
                file_path = os.path.join(test_project_dir, filename)
                arkts_analyzer.update_file_knowledge_graph(file_path)
        
        # Check results
        files = database.get_all_files()
        classes = database.get_all_classes()
        
        print(f"   ✓ Successfully processed {len(files)} files")
        print(f"   ✓ Found {len(classes)} classes/components")
        
        # Cleanup
        if os.path.exists(database.DATABASE_PATH):
            os.remove(database.DATABASE_PATH)
        shutil.rmtree(test_dir)
        
        return True
    except Exception as e:
        print(f"   ✗ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    results = []
    
    results.append(("Database", test_database()))
    results.append(("ArkTS Analyzer", test_arkts_analyzer()))
    results.append(("File Monitor", test_file_monitor()))
    results.append(("LLM Handler", test_llm_handler()))
    results.append(("API Structure", test_api_endpoints()))
    results.append(("End-to-end Workflow", test_end_to_end_workflow()))
    
    print("\n" + "=" * 60)
    print("  Summary")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        status_icon = "✓" if passed else "✗"
        print(f"  {status_icon} {name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("  All tests passed! ✓")
    else:
        print("  Some tests failed! ✗")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
