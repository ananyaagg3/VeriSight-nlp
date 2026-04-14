# 🚀 Quick Start Guide

## ✅ System is Running!

### Current Status
- ✅ **Frontend**: Running at http://localhost:5173
- ✅ **Backend**: Running at http://localhost:8000
- ⚠️ **ML Models**: Will download on first use (requires internet)

## 🌐 Access the Application

**Open your browser and visit:**
```
http://localhost:5173
```

You should see the premium UI with:
- Dark/Light mode toggle
- Text input area
- Language selector (15 languages)
- File upload option

## 🧪 Test the System

### Quick Test
1. Enter some text in the input area (minimum 10 characters)
2. Select a language
3. Click "Analyze for Misinformation"
4. Wait for results (first time may take longer as models download)

### Example Texts to Try

**Authentic News:**
```
The World Health Organization announced new guidelines for public health safety measures.
```

**Suspicious Pattern:**
```
Click here now! You won't believe this shocking truth doctors don't want you to know!
```

## 📊 API Documentation

Visit the interactive API docs:
```
http://localhost:8000/docs
```

## 🔧 Configuration

### Add MongoDB (Optional)
1. Create free MongoDB Atlas account
2. Get connection string
3. Edit `.env` file:
```env
MONGODB_URI=your_mongodb_connection_string
```

### Add Google Fact Check API (Optional)
1. Get API key from Google Cloud Console
2. Edit `.env` file:
```env
GOOGLE_FACT_CHECK_KEY=your_api_key
```

## 🎨 Features to Explore

### Dark Mode
- Click the 🌙/☀️ button in the navbar

### File Upload
- Upload .txt or .md files instead of typing

### History
- Click "History" in navbar to see past analyses

### About Page
- Click "About" to see full feature list

### Feedback
- After each analysis, rate the accuracy

## 🐛 Troubleshooting

### Backend Issues
If backend crashes, restart it:
```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

### Frontend Issues
If frontend has issues:
```powershell
cd frontend
npm run dev
```

### Model Download Issues
- First analysis will download models (~2GB)
- Requires internet connection
- May take 5-10 minutes
- Models are cached after first download

## 📝 Next Steps

1. **Test the UI** - Try analyzing different texts
2. **Explore features** - Dark mode, file upload, history
3. **Add MongoDB** - For persistent storage
4. **Add API keys** - For knowledge graph features
5. **Train custom models** - See `ml-models/` directory

## 🎯 Production Deployment

When ready to deploy:

**Frontend (Vercel):**
```bash
cd frontend
vercel deploy --prod
```

**Backend (Railway):**
```bash
cd backend
railway deploy --prod
```

## 💡 Tips

- **First run**: Models download automatically (be patient!)
- **Offline mode**: Works without MongoDB/API keys
- **Fast mode**: After first run, analysis is ~200ms
- **Mobile**: UI is fully responsive

---

**Enjoy your AI-powered fact-checking system! 🎉**
