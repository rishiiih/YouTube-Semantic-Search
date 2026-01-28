# YouTube Semantic Search - Multi-Modal RAG System

<div align="center">


**A powerful Multi-Modal Retrieval-Augmented Generation (RAG) system that enables semantic search and Q&A across YouTube video content with timestamp-accurate responses.**

</div>

---

## 🎯 Overview

YouTube Semantic Search is an advanced AI-powered system that transforms how users interact with YouTube video content. By combining state-of-the-art Natural Language Processing (NLP) with vector embeddings and Large Language Models (LLMs), it enables users to ask natural language questions about video content and receive accurate, timestamp-referenced answers.

### What Makes It Special?

- 🎥 **Unlimited Video Length Support** - Process videos of any duration without length restrictions
- 🔍 **Semantic Understanding** - Goes beyond keyword matching to understand context and meaning
- ⏱️ **Timestamp Precision** - Every answer includes clickable timestamps that jump directly to relevant video sections
- 🤖 **AI-Powered Responses** - Leverages Groq's Llama 3.3 70B model for intelligent, context-aware answers
- 📊 **Real-Time Progress Tracking** - Monitor video processing status with detailed progress indicators

---

## ✨ Key Features

### 🎬 Video Ingestion & Processing

- **Multi-Source Transcript Extraction**
  - Primary: YouTube's official Transcript API (fastest, no download required)
  - Fallback: Automatic audio download + Groq Whisper Large V3 transcription
  - Smart chunking for unlimited video lengths (handles hours-long content)

- **Metadata Extraction**
  - Video title, thumbnail, channel name
  - Upload date, view count, duration
  - Automatic fetching via yt-dlp

- **Real-Time Progress Tracking**
  - 8-step ingestion pipeline with percentage completion
  - Live status updates: Fetching metadata → Transcribing → Embedding → Indexing
  - Visual progress bars in the UI

### 🔍 Semantic Search & RAG

- **Advanced Vector Search**
  - Sentence-BERT embeddings (all-MiniLM-L6-v2)
  - ChromaDB vector database for fast similarity search
  - Configurable top-k retrieval (default: 20 chunks)

- **Intelligent Q&A**
  - Context-aware responses using Groq Llama 3.3 70B
  - Multi-chunk reasoning for comprehensive answers
  - Chronologically sorted timestamps with clickable links
  - Source attribution with exact time references

- **Timestamp Extraction & Sorting**
  - Automatic extraction of [MM:SS] and [HH:MM:SS] formats
  - Chronological ordering of timestamps in responses
  - Direct YouTube player integration (click to jump)

### 📚 Video Library Management

- **Complete Video Dashboard**
  - Grid layout with thumbnail previews
  - Status indicators (Pending, Processing, Completed, Failed)
  - Metadata display: channel, views, duration, upload date
  - Progress tracking for processing videos


### 📊 Analytics & Insights

- **System Statistics**
  - Total videos processed
  - Total transcription duration
  - Average video length
  - Processing success rate

- **Performance Metrics**
  - Storage usage tracking
  - Query response times
  - Most searched videos
  - Popular questions

### 🎨 Modern UI/UX

- **Dark Mode Design**
  - Custom dark green theme (#16a34a)
  - High contrast for readability
  - Smooth animations and transitions


- **Component Library**
  - shadcn/ui components
  - Radix UI primitives
  - Tailwind CSS styling
  - Lucide React icons

### 🔧 Developer Features

- **Type Safety**
  - Full TypeScript implementation
  - Zod schema validation
  - Type-safe API contracts

- **State Management**
  - Zustand for global state
  - TanStack Query for server state
  - Optimistic updates

- **Error Handling**
  - Graceful degradation
  - User-friendly error messages
  - Automatic retry logic

---

## 🛠️ Tech Stack

### Backend

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Core language | 3.11+ |
| **FastAPI** | Web framework | 0.109.0 |
| **Groq** | LLM & Whisper API | Latest |
| **ChromaDB** | Vector database | 0.5.23 |
| **SQLite** | Relational database | Built-in |
| **Sentence-Transformers** | Embedding generation | 2.3.1 |
| **yt-dlp** | YouTube video/audio download | 2025.12.8+ |
| **youtube-transcript-api** | Transcript extraction | 0.6.2 |
| **FFmpeg** | Audio processing | Latest |
| **Pydantic** | Data validation | 2.10.5 |
| **aiosqlite** | Async SQLite support | 0.19.0 |
| **uvicorn** | ASGI server | 0.27.0 |

### Frontend

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 18.3.1 |
| **TypeScript** | Type safety | 5.5.3 |
| **Vite** | Build tool | 5.4.2 |
| **Tailwind CSS** | Styling | 3.4.1 |
| **shadcn/ui** | Component library | Latest |
| **Radix UI** | Primitives | Latest |
| **TanStack Query** | Data fetching | 5.56.2 |
| **Zustand** | State management | 5.0.0 |
| **Axios** | HTTP client | 1.6.7 |
| **React Hot Toast** | Notifications | 2.4.1 |
| **Lucide React** | Icons | Latest |

### AI/ML Models

- **LLM**: Groq Llama 3.3 70B Versatile
- **Transcription**: Groq Whisper Large V3 Turbo
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Vector Search**: ChromaDB with HNSW indexing

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────┐   │
│  │  Ingest  │  │ Library  │  │  Search  │  │  Analytics  │   │
│  │   Tab    │  │   Tab    │  │   Tab    │  │     Tab     │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬──────┘   │
│       │             │              │               │           │
│       └─────────────┴──────────────┴───────────────┘           │
│                          │                                      │
│                     TanStack Query                              │
│                          │                                      │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                      FastAPI REST API
                           │
┌──────────────────────────┼──────────────────────────────────────┐
│                    Backend (Python)                              │
│                          │                                       │
│  ┌───────────────────────┴──────────────────────┐              │
│  │            Ingestion Pipeline                 │              │
│  │  1. Extract Video ID                          │              │
│  │  2. Fetch Metadata (yt-dlp)                   │              │
│  │  3. Get Transcript (YouTube API/Whisper)      │              │
│  │  4. Chunk Text (300 tokens, 50 overlap)       │              │
│  │  5. Generate Embeddings (Sentence-BERT)       │              │
│  │  6. Store in ChromaDB + SQLite                │              │
│  │  7. Generate Question Suggestions (Llama)     │              │
│  └───────────────────────────────────────────────┘              │
│                          │                                       │
│  ┌───────────────────────┴──────────────────────┐              │
│  │            Query Pipeline                     │              │
│  │  1. Embed Question (Sentence-BERT)            │              │
│  │  2. Vector Search (ChromaDB top-k=20)         │              │
│  │  3. Retrieve Context Chunks                   │              │
│  │  4. Build Prompt with Context                 │              │
│  │  5. Generate Answer (Groq Llama 3.3)          │              │
│  │  6. Extract & Sort Timestamps                 │              │
│  │  7. Return Structured Response                │              │
│  └───────────────────────────────────────────────┘              │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────┐       │
│  │   ChromaDB   │  │    SQLite    │  │  Groq API      │       │
│  │   (Vectors)  │  │  (Metadata)  │  │  (LLM/Whisper) │       │
│  └──────────────┘  └──────────────┘  └────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

### Database Schema

**SQLite Tables:**
```sql
-- Videos table
CREATE TABLE videos (
    video_id TEXT PRIMARY KEY,
    youtube_url TEXT NOT NULL,
    title TEXT,
    duration REAL,
    thumbnail_url TEXT,
    channel_name TEXT,
    upload_date TEXT,
    view_count INTEGER,
    status TEXT,
    progress_step TEXT,
    progress_percent REAL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Transcripts table
CREATE TABLE transcripts (
    id INTEGER PRIMARY KEY,
    video_id TEXT,
    segment_index INTEGER,
    text TEXT,
    start_time REAL,
    end_time REAL,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

-- Chunks table
CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    video_id TEXT,
    text TEXT,
    start_time REAL,
    end_time REAL,
    chunk_index INTEGER,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);

-- Question suggestions table
CREATE TABLE question_suggestions (
    id INTEGER PRIMARY KEY,
    video_id TEXT,
    question TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
);
```

**ChromaDB Collections:**
- Collection per video: `video_{video_id}`
- Metadata: chunk_id, chunk_index, start_time, end_time
- Embeddings: 384-dimensional vectors (all-MiniLM-L6-v2)

---

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg (for audio processing)
- Groq API Key ([Get one here](https://console.groq.com))

### Backend Setup

1. **Clone the repository**
```bash
git clone https://github.com/rishiiih/youtube-semantic-search.git
cd youtube-semantic-search
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

5. **Initialize database**
```bash
python backend/migrate_db.py
```

6. **Run backend server**
```bash
uvicorn backend.app.main:app --reload
# Server runs on http://localhost:8000
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure API URL**
```bash
# Create .env.local
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

4. **Run development server**
```bash
npm run dev
# Frontend runs on http://localhost:5173


---

## 📖 Usage

### 1. Ingest a Video

1. Go to the **Ingest** tab
2. Paste a YouTube URL (e.g., `https://www.youtube.com/watch?v=dQw4w9WgXcQ`)
3. Click **Ingest Video**
4. Monitor progress in real-time

### 2. Browse Your Library

1. Navigate to the **Library** tab
2. View all processed videos with thumbnails and metadata
3. Click on any video card to see details

### 3. Search & Ask Questions

1. Go to the **Search** tab
2. Select a video from the dropdown
3. Ask questions like:
   - "What is the main topic discussed?"
   - "Summarize the key points"
   - "When does the speaker talk about X?"
4. Click timestamps to jump to specific moments in the video

### 4. View Analytics

1. Open the **Analytics** tab
2. See system-wide statistics
3. Monitor processing trends

---

## 🙏 Acknowledgments

- **Groq** - For lightning-fast LLM and Whisper inference
- **ChromaDB** - For efficient vector storage and retrieval
- **shadcn/ui** - For beautiful UI components
- **YouTube** - For providing transcript APIs
- **Hugging Face** - For sentence-transformers models

---

<div align="center">

Made with ❤️ by Rishiraj Singh

</div>
