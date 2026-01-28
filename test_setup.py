"""
Test script to validate Phase 1 setup
Run: python test_setup.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_config():
    """Test configuration loading"""
    print("✓ Testing configuration...")
    from backend.app.config import settings
    
    print(f"  - Environment: {settings.environment}")
    print(f"  - LLM Provider: {settings.llm_provider}")
    print(f"  - Groq API Key: {'✓ Set' if settings.groq_api_key else '✗ Missing'}")
    print(f"  - ChromaDB Path: {settings.chroma_path}")
    print(f"  - SQLite Path: {settings.sqlite_db_path}")
    
    if not settings.groq_api_key:
        print("  ⚠ Warning: GROQ_API_KEY not set in .env")
    
    return True


async def test_database():
    """Test SQLite database initialization"""
    print("\n✓ Testing SQLite database...")
    from backend.database.db import db, init_db
    
    # Initialize database
    await init_db()
    print("  - Database initialized")
    
    # Check health
    is_healthy = await db.check_health()
    print(f"  - Database health: {'✓ OK' if is_healthy else '✗ Failed'}")
    
    # Check tables exist
    conn = await db.get_connection()
    try:
        cursor = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in await cursor.fetchall()]
        print(f"  - Tables created: {', '.join(tables)}")
    finally:
        await conn.close()
    
    return is_healthy


async def test_chromadb():
    """Test ChromaDB initialization"""
    print("\n✓ Testing ChromaDB...")
    import chromadb
    from backend.app.config import settings
    
    # Initialize client
    client = chromadb.PersistentClient(path=settings.chroma_path)
    print(f"  - ChromaDB initialized at: {settings.chroma_path}")
    
    # Create test collection
    try:
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"description": "Test collection"}
        )
        print(f"  - Test collection created: {collection.name}")
        
        # Clean up
        client.delete_collection("test_collection")
        print("  - Test collection deleted")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def test_embedding_model():
    """Test sentence-transformers model"""
    print("\n✓ Testing embedding model...")
    from sentence_transformers import SentenceTransformer
    from backend.app.config import settings
    
    try:
        model = SentenceTransformer(settings.embedding_model)
        print(f"  - Model loaded: {settings.embedding_model}")
        
        # Test embedding
        test_text = "This is a test sentence"
        embedding = model.encode(test_text)
        print(f"  - Embedding dimension: {len(embedding)}")
        
        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


async def main():
    print("=" * 60)
    print("Phase 1 Setup Validation")
    print("=" * 60)
    
    results = []
    
    try:
        results.append(("Config", await test_config()))
        results.append(("Database", await test_database()))
        results.append(("ChromaDB", await test_chromadb()))
        results.append(("Embeddings", await test_embedding_model()))
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:.<20} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Ready for Phase 2.")
    else:
        print("\n⚠ Some tests failed. Fix issues before proceeding.")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
