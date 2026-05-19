
#!/usr/bin/env python3
"""
Realistic Integration Test - Simulates a real user scenario
"""
import os
import sys
import tempfile
import shutil
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import database
import arkts_analyzer
from file_monitor import FileMonitorService


def run_realistic_test():
    """Run a realistic integration test"""
    print("=" * 70)
    print("🚀 REALISTIC INTEGRATION TEST - Simulating Real Usage")
    print("=" * 70)

    # Create a temporary test project
    with tempfile.TemporaryDirectory(prefix="arkts_integration_test_") as temp_dir:
        temp_path = Path(temp_dir)
        test_project = temp_path / "test_project"
        test_project.mkdir()

        print(f"\n📁 Test project: {test_project}")

        # Set up custom database
        db_path = temp_path / "integration_test.db"
        database.set_custom_db_path(str(db_path))
        database.init_database()
        print("✓ Database initialized")

        # --- Scenario 1: Initial Project Setup ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 1: Initial project with 5 files")
        print("-" * 70)
        create_sample_file(test_project / "App.ets", "App", "class App { aboutToAppear() {} onDestroy() {} }")
        create_sample_file(test_project / "HomePage.ets", "HomePage", "struct HomePage { build() { } }")
        create_sample_file(test_project / "UserProfile.ets", "UserProfile", "struct UserProfile { build() { Text('Profile') } }")
        create_sample_file(test_project / "Products.ets", "Products", "struct Products { build() { } }")
        create_sample_file(test_project / "Settings.ets", "Settings", "struct Settings { build() { } }")

        # Initial sync
        monitor = FileMonitorService(str(test_project), 1000)
        monitor.initial_sync()
        print("✓ Initial sync complete")

        # Verify
        files = database.get_all_files()
        assert len(files) == 5, f"Expected 5 files, got {len(files)}"
        print(f"✓ Verified: {len(files)} files found")

        classes = database.get_all_classes()
        assert len(classes) == 5, f"Expected 5 classes, got {len(classes)}"
        print(f"✓ Verified: {len(classes)} classes found")

        # --- Scenario 2: Modify a file ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 2: Modify a file")
        print("-" * 70)
        create_sample_file(test_project / "HomePage.ets", "HomePage", """struct HomePage {
  @State message: string = 'Welcome'
  build() {
    Column() {
      Text(this.message)
    }
  }
  updateMessage(msg: string) {
    this.message = msg
  }
}""")

        # Simulate update
        arkts_analyzer.update_file_knowledge_graph(str(test_project / "HomePage.ets"))

        # Check
        classes = database.get_all_classes()
        home_class = next(c for c in classes if c["name"] == "HomePage")
        assert home_class is not None, "HomePage class not found"
        print("✓ File modified successfully")

        # --- Scenario 3: Add 3 more files ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 3: Add 3 more files")
        print("-" * 70)
        create_sample_file(test_project / "Cart.ets", "Cart", "struct Cart { build() { } addItem() {} }")
        create_sample_file(test_project / "Checkout.ets", "Checkout", "struct Checkout { build() { } processPayment() {} }")
        create_sample_file(test_project / "API.ets", "API", "class API { fetchProducts() {} fetchUser() {} }")

        for file in ["Cart.ets", "Checkout.ets", "API.ets"]:
            arkts_analyzer.update_file_knowledge_graph(str(test_project / file))

        files = database.get_all_files()
        assert len(files) == 8, f"Expected 8 files, got {len(files)}"
        print(f"✓ Files added - total now: {len(files)}")

        # --- Scenario 4: Delete a file ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 4: Delete a file")
        print("-" * 70)
        settings_path = test_project / "Settings.ets"
        existing_file = database.get_file_by_path(str(settings_path))
        if existing_file:
            database.delete_file_data(existing_file["id"])

        files = database.get_all_files()
        assert len(files) == 7, f"Expected 7 files, got {len(files)}"
        print(f"✓ File deleted - total now: {len(files)}")

        # --- Scenario 5: Repeated modifications ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 5: Multiple rapid modifications")
        print("-" * 70)
        for i in range(3):
            create_sample_file(
                test_project / "Products.ets",
                "Products",
                f"""struct Products {{
  count: number = {i}
  build() {{ Text('Products: ' + this.count) }}
  refresh() {{ }}
}}"""
            )
            arkts_analyzer.update_file_knowledge_graph(str(test_project / "Products.ets"))
        print("✓ Rapid modifications handled")

        # --- Scenario 6: Check data integrity ---
        print("\n" + "-" * 70)
        print("📝 SCENARIO 6: Check data integrity")
        print("-" * 70)

        classes = database.get_all_classes()
        methods = database.get_all_methods()
        files = database.get_all_files()

        # Verify no orphaned classes (all should have file_id)
        for cls in classes:
            file_exists = any(f["id"] == cls["file_id"] for f in files)
            assert file_exists, f"Class {cls['name']} has orphaned file_id {cls['file_id']}"

        # Verify no orphaned methods
        for method in methods:
            class_exists = any(c["id"] == method["class_id"] for c in classes)
            assert class_exists, f"Method {method['name']} has orphaned class_id {method['class_id']}"

        print("✓ Data integrity verified")

        # --- Final Check ---
        print("\n" + "-" * 70)
        print("📝 FINAL CHECK")
        print("-" * 70)

        print(f"Files: {len(files)}")
        print(f"Classes: {len(classes)}")
        print(f"Methods: {len(methods)}")

        print("\n" + "=" * 70)
        print("✅ ALL REALISTIC INTEGRATION TESTS PASSED!")
        print("=" * 70)


def create_sample_file(file_path: Path, class_name: str, content: str):
    """Create a sample ArkTS file"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Created: {file_path.name}")


if __name__ == "__main__":
    run_realistic_test()
