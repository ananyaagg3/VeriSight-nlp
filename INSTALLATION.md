# 🚀 Complete Installation Guide
## Explainable Multimodal Misinformation Detection System

This guide will help you set up the complete project from scratch.

## ⚡ Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** and npm ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **10+ GB free disk space** (for ML models)
- **Stable internet connection** (for model downloads)

### Step 1: Clone the Repository

```bash
cd explainable-misinformation-detection
```

---

## 🔧 Backend Setup

### 1. Create Python Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note:** If you encounter errors with torch installation, install it separately first:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### 3. Download spaCy Multilingual Model

```bash
python -m spacy download xx_ent_wiki_sm
```

### 4. Download ML Models (Automatic)

Run the setup script to download all models:
```bash
python setup_models.py
```

This will download (~2-3 GB total):
- ✅ XLM-RoBERTa (~1.1 GB)
- ✅ CLIP (~600 MB)
- ✅ FLAVA (~900 MB)
- ✅ spaCy multilingual (~500 MB)

**Time estimate:** 10-30 minutes depending on internet speed

---

## 🎨 Frontend Setup

### 1. Navigate to Frontend

```bash
cd ../frontend
```

### 2. Install npm Dependencies

```bash
npm install
```

This installs:
- React, React Router
- Axios for API calls
- Recharts for visualizations
- Framer Motion for animations
- Tailwind CSS for styling
- i18next for multilingual support

---

## 🔐 Configuration

### 1. Backend Environment Variables

Create `.env` file in the project root:

```bash
cd ..
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` and configure:

```env
# REQUIRED: MongoDB Connection
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/misinformation_db?retryWrites=true&w=majority

# RECOMMENDED: Google Fact Check API
GOOGLE_FACT_CHECK_KEY=your_google_api_key_here

# URLs (default values work for local development)
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Optional
REDIS_URL=redis://localhost:6379
NEWS_API_KEY=your_news_api_key_here
LOG_LEVEL=INFO
```

### 2. Get API Keys

#### MongoDB Atlas (Required)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create free account
3. Create new cluster (FREE M0 tier - 512MB)
4. Database Access → Add New User
5. Network Access → Add IP Address (0.0.0.0/0 for development)
6. Clusters → Connect → Connect your application
7. Copy connection string to `.env`

#### Google Fact Check API (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable "Fact Check Tools API"
4. Credentials → Create Credentials → API Key
5. Copy API key to `.env`

**Free tier:** 1000 requests/day

### 3. Frontend Environment (Optional)

Create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Running the Application

### Terminal 1: Start Backend

```bash
cd backend
# Activate virtual environment first
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate # Linux/Mac

# Start server
python -m uvicorn app.main:app --reload
```

**Backend will start on:** http://localhost:8000
**API Documentation:** http://localhost:8000/docs

### Terminal 2: Start Frontend

```bash
cd frontend
npm run dev
```

**Frontend will start on:** http://localhost:5173

---

## ✅ Verification

### 1. Backend Health Check

Visit: http://localhost:8000/health

Expected response:
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### 2. Frontend Check

Visit: http://localhost:5173

You should see the misinformation detection dashboard.

### 3. Test Analysis

1. Enter sample text: "Scientists discover cure for all diseases using this one simple trick!"
2. Select language: English
3. Click "Analyze"
4. You should see results with confidence score and verdict

---

## 🎯 Features Available

✅ **Multilingual Text Analysis** - 15+ languages supported
✅ **Image Upload & Analysis** - Upload images for authenticity check
✅ **Multimodal Fusion** - Combined text + image analysis
✅ **Knowledge Graph Verification** - Wikidata + Google Fact Check
✅ **Confidence Visualizations** - Charts and graphs
✅ **Evidence Keywords** - Attention-weighted terms
✅ **Source Links** - Fact-checking sources
✅ **Analysis History** - View past analyses
✅ **Dark Mode** - Toggle theme

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "No module named 'app'"**
- Make sure you're in the `backend` directory
- Virtual environment is activated
- Dependencies are installed

**Error: "ModuleNotFoundError: transformers"**
```bash
pip install transformers torch
```

**Error: "MongoDB connection failed"**
- Check `MONGODB_URI` in `.env`
- Verify MongoDB Atlas IP whitelist includes your IP
- Test connection string in MongoDB Compass

### Models not loading

**Error: "Could not load model"**
- Run `python setup_models.py` again
- Check internet connection
- Ensure 10+ GB free disk space

**Models download slowly**
- This is normal, models are large
- First startup takes 10-30 minutes
- Subsequent startups are instant (cached)

### Frontend issues

**Error: "Failed to fetch"**
- Check backend is running on port 8000
- Verify `VITE_API_URL` in `frontend/.env.local`
- Check browser console for CORS errors

**Charts not displaying**
- Clear browser cache
- Check recharts is installed: `npm list recharts`
- Reinstall: `npm install recharts`

### Performance issues

**Analysis is slow (>5 seconds)**
- First analysis takes longer (model loading)
- Subsequent analyses should be <300ms
- Check CPU usage - ML inference is CPU-intensive
- Consider using GPU by changing device in `ml_pipeline.py`

---

## 📊 API Keys Summary

| Service | Required? | Free Tier | Sign Up | Purpose |
|---------|-----------|-----------|---------|---------|
| **MongoDB Atlas** | ✅ Yes | 512MB | [Sign up](https://www.mongodb.com/cloud/atlas/register) | Database |
| **Google Fact Check** | ⭐ Recommended | 1000/day | [Get key](https://developers.google.com/fact-check/tools/api) | Verification |
| Wikidata | No key needed | 5000/hour | N/A | Entity info |
| News API | Optional | 100/day | [Sign up](https://newsapi.org/) | Testing |

---

##🎓 Next Steps

1. **Test Different Languages** - Try Hindi, Spanish, French, Arabic
2. **Upload Images** - Test multimodal analysis
3. **Check History** - View past analyses
4. **Review Sources** - Click on verification sources
5. **Submit Feedback** - Help improve the system

---

## 📚 Additional Resources

- **API Documentation:** http://localhost:8000/docs
- **Model Information:** See `COMPLETE_PROJECT_DOCUMENT.md`
- **Architecture Details:** See `implementation_plan.md`

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide's troubleshooting section
2. Review console/terminal errors
3. Check backend logs
4. Verify all environment variables are set
5. Ensure all dependencies installed correctly

---

## 🎉 Success!

You should now have a fully functional explainable multimodal misinformation detection system running locally!

**Happy fact-checking! 🚀**
