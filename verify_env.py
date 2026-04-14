import sys
import importlib
import pkg_resources

REQUIRED_PACKAGES = [
    "fastapi",
    "uvicorn",
    "motor",
    "spacy",
    "torch",
    "transformers",
    "sentence_transformers",
    "PIL",
    "numpy",
    "requests",
    "pydantic",
    "pydantic_settings"
]

def check_imports():
    print("🔍 Verifying Python Environment & Dependencies...")
    print(f"Python Version: {sys.version.split()[0]}")
    
    all_passed = True
    missing = []
    
    for package in REQUIRED_PACKAGES:
        try:
            # Handle special import names
            import_name = package
            if package == "PIL": import_name = "PIL"
            if package == "sentence_transformers": import_name = "sentence_transformers"
            
            importlib.import_module(import_name)
            
            try:
                version = pkg_resources.get_distribution(package).version
                print(f"✅ {package:<25} v{version}")
            except:
                print(f"✅ {package:<25} (installed)")
                
        except ImportError:
            print(f"❌ {package:<25} NOT FOUND")
            missing.append(package)
            all_passed = False
        except Exception as e:
            print(f"⚠️ {package:<25} ERROR: {e}")
            all_passed = False

    print("-" * 40)
    if all_passed:
        print("✨ All critical dependencies are installed!")
        return True
    else:
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    check_imports()
