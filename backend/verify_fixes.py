import sys
import asyncio
import logging
from PIL import Image
import io
import torch

# Add current directory to path
sys.path.append(".")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verifier")

async def verify():
    print("="*60)
    print("🧪 STARTING VERIFICATION")
    print("="*60)

    try:
        from app.services.ml_pipeline import ml_pipeline
        
        # 1. Test Model Loading
        print("\n[1/3] Checking Models...")
        if ml_pipeline.models_loaded:
            print("✅ Models loaded successfully")
        else:
            print("⚠️ Models failed to load (this is expected if no internet/cache, but let's check fallback)")

        # 2. Test Multilingual Text (Hindi)
        print("\n[2/3] Testing Multilingual Support (Hindi)...")
        hindi_text = "यह एक फर्जी खबर है कि पृथ्वी चपटी है।" # "It is fake news that earth is flat"
        result = await ml_pipeline.run_pipeline(text=hindi_text, language="hi")
        
        print(f"Verdict: {result['verdict']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Keywords: {result['keywords']}")
        
        if result['verdict'] in ["MISINFORMATION", "UNCERTAIN"]:
            print("✅ Hindi text analysis working (or falling back correctly)")
        else:
            print(f"❓ Unexpected result for Hindi: {result}")

        # 3. Test Image Analysis (CLIP Zero-Shot)
        print("\n[3/3] Testing Image Authenticity...")
        # Create a red square
        img = Image.new('RGB', (200, 200), color = 'red')
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        img_bytes = buf.getvalue()
        
        # Analyze directly
        img_result = await ml_pipeline.image_analysis(image_data=img_bytes)
        
        if img_result:
            print(f"Authenticity Score: {img_result['authenticity']}")
            print(f"Manipulation Score: {img_result.get('manipulation_score')}")
            
            if img_result['authenticity'] != 0.85:
                print("✅ Image analysis is DYNAMIC (not hardcoded 0.85)")
            else:
                print("❌ Image analysis is still HARDCODED")
        else:
            print("❌ Image analysis failed (model likely not loaded)")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you are running this from 'backend' directory")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(verify())
