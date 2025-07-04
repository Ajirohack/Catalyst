"""
Performance benchmark tests for the Catalyst backend.
These tests measure the performance of key operations and compare against baseline thresholds.
"""
import os
import sys
import time
import pytest
import psutil
import random
import uuid
from datetime import datetime
from typing import Dict, List, Any

# Add the backend directory to the Python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

# Conditionally import services to avoid errors when not available
try:
    from services.analysis_service import AnalysisService
    analysis_available = True
except ImportError:
    analysis_available = False

try:
    from services.knowledge_base_service import KnowledgeBaseService
    from services.file_service import FileService
    kb_available = True
except ImportError:
    kb_available = False


class MemoryMonitor:
    """Memory usage monitoring utility for performance tests."""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.start_memory = 0
        self.peak_memory = 0
        self.end_memory = 0
    
    def start(self):
        """Start monitoring memory usage."""
        self.start_memory = self.process.memory_info().rss
        self.peak_memory = self.start_memory
        return self.start_memory
    
    def check(self):
        """Check current memory usage and update peak if needed."""
        current = self.process.memory_info().rss
        if current > self.peak_memory:
            self.peak_memory = current
        return current
    
    def stop(self):
        """Stop monitoring and return memory usage statistics."""
        self.end_memory = self.process.memory_info().rss
        return {
            "start_memory_mb": self.start_memory / (1024 * 1024),
            "peak_memory_mb": self.peak_memory / (1024 * 1024),
            "end_memory_mb": self.end_memory / (1024 * 1024),
            "memory_increase_mb": (self.end_memory - self.start_memory) / (1024 * 1024)
        }


class TimingContext:
    """Context manager for timing operations."""
    
    def __init__(self, name):
        self.name = name
        self.start_time = 0
        self.end_time = 0
        self.memory_monitor = MemoryMonitor()
    
    def __enter__(self):
        self.start_time = time.time()
        self.memory_monitor.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        memory_stats = self.memory_monitor.stop()
        
        # Print timing and memory information
        elapsed = self.end_time - self.start_time
        print(f"\n--- {self.name} Performance ---")
        print(f"Execution time: {elapsed:.4f} seconds")
        print(f"Memory usage (start): {memory_stats['start_memory_mb']:.2f} MB")
        print(f"Memory usage (peak): {memory_stats['peak_memory_mb']:.2f} MB")
        print(f"Memory usage (end): {memory_stats['end_memory_mb']:.2f} MB")
        print(f"Memory increase: {memory_stats['memory_increase_mb']:.2f} MB")
        
        self.stats = {
            "execution_time": elapsed,
            **memory_stats
        }


@pytest.fixture
def performance_context():
    """Fixture to provide a timing context for performance tests."""
    def _context_factory(name):
        return TimingContext(name)
    return _context_factory


@pytest.mark.performance
class TestAnalysisPerformance:
    """Performance tests for analysis operations."""
    
    @pytest.mark.skipif(not analysis_available, reason="Analysis service not available")
    def test_sentiment_analysis_performance(self, performance_context, 
                                           performance_thresholds):
        """Test the performance of sentiment analysis."""
        # Generate test data: a conversation with varying lengths
        sizes = [
            ("small", 500),      # ~500 chars
            ("medium", 5000),    # ~5000 chars
            ("large", 50000)     # ~50000 chars
        ]
        
        results = {}
        
        for size_name, char_count in sizes:
            # Generate a conversation of approximately the target size
            conversation = self._generate_conversation(char_count)
            
            # Initialize the service
            analysis_service = AnalysisService()
            
            # Perform the analysis with timing
            with performance_context(f"Sentiment Analysis ({size_name})") as context:
                result = analysis_service.analyze_sentiment(conversation)
            
            # Store the results
            results[size_name] = {
                "execution_time": context.stats["execution_time"],
                "memory_increase_mb": context.stats["memory_increase_mb"],
                "text_size": len(conversation)
            }
            
            # Verify against thresholds
            threshold = performance_thresholds["analysis"]["sentiment"][size_name]["max_time"]
            assert context.stats["execution_time"] < threshold, \
                f"Sentiment analysis for {size_name} text exceeded time threshold: " \
                f"{context.stats['execution_time']:.2f}s > {threshold:.2f}s"
        
        # Print comparative results
        print("\n--- Sentiment Analysis Performance Summary ---")
        for size_name in ["small", "medium", "large"]:
            stats = results[size_name]
            print(f"{size_name.capitalize()} text ({stats['text_size']} chars): "
                  f"{stats['execution_time']:.4f}s, "
                  f"Memory: {stats['memory_increase_mb']:.2f} MB")
    
    def _generate_conversation(self, target_size):
        """Generate a conversation of approximately the target size."""
        templates = [
            "Hello, how are you today?",
            "I've been feeling {emotion} lately because of {reason}.",
            "That's interesting. Have you tried {suggestion}?",
            "Yes, I did. It made me feel {emotion}.",
            "I think we should discuss {topic} more often.",
            "I {agreement} with that. {elaboration}",
            "What do you think about {topic}?",
            "In my opinion, {opinion}.",
            "Let's plan to {activity} sometime next week.",
            "That sounds {evaluation}! I'm looking forward to it."
        ]
        
        emotions = ["happy", "sad", "anxious", "excited", "calm", "frustrated", "hopeful"]
        reasons = ["work", "family", "health", "the weather", "recent events", "personal goals"]
        suggestions = ["meditation", "exercise", "talking to friends", "taking a break", "journaling"]
        topics = ["communication", "future plans", "feelings", "shared interests", "past experiences"]
        agreements = ["agree", "disagree", "partially agree", "completely agree", "somewhat disagree"]
        elaborations = [
            "It's important for our relationship.",
            "I've been thinking about this for a while.",
            "This could really help us grow together.",
            "I need some time to process this fully.",
            "We should revisit this conversation later."
        ]
        opinions = [
            "it's a good idea to take things slowly",
            "we need to be more open with each other",
            "it's better to address issues as they arise",
            "regular check-ins would benefit our relationship",
            "focusing on positive experiences helps build connection"
        ]
        activities = ["have dinner", "go for a walk", "watch a movie", "visit the park", "try that new restaurant"]
        evaluations = ["great", "wonderful", "perfect", "excellent", "fantastic"]
        
        speakers = ["Alice", "Bob"]
        conversation = ""
        current_size = 0
        
        while current_size < target_size:
            speaker = random.choice(speakers)
            template = random.choice(templates)
            
            # Fill in the template with random values
            message = template.format(
                emotion=random.choice(emotions),
                reason=random.choice(reasons),
                suggestion=random.choice(suggestions),
                topic=random.choice(topics),
                agreement=random.choice(agreements),
                elaboration=random.choice(elaborations),
                opinion=random.choice(opinions),
                activity=random.choice(activities),
                evaluation=random.choice(evaluations)
            )
            
            # Add to conversation
            line = f"{speaker}: {message}\n"
            conversation += line
            current_size += len(line)
        
        return conversation


@pytest.mark.performance
class TestKnowledgeBasePerformance:
    """Performance tests for knowledge base operations."""
    
    @pytest.mark.skipif(not kb_available, reason="Knowledge base service not available")
    def test_document_indexing_performance(self, performance_context, 
                                         performance_thresholds, temp_storage):
        """Test the performance of document indexing operations."""
        # Initialize services
        storage_service_path = os.path.join(temp_storage, "kb_test")
        os.makedirs(storage_service_path, exist_ok=True)
        
        kb_service = KnowledgeBaseService(storage_dir=storage_service_path)
        
        # Test sizes
        sizes = [
            ("small", 10),      # 10 documents
            ("medium", 50),     # 50 documents
            ("large", 200)      # 200 documents
        ]
        
        results = {}
        
        for size_name, doc_count in sizes:
            # Generate test documents
            documents = self._generate_test_documents(doc_count)
            
            # Perform indexing with timing
            with performance_context(f"Document Indexing ({size_name})") as context:
                for doc in documents:
                    kb_service.add_document(doc)
            
            # Store the results
            results[size_name] = {
                "execution_time": context.stats["execution_time"],
                "memory_increase_mb": context.stats["memory_increase_mb"],
                "doc_count": doc_count,
                "avg_time_per_doc": context.stats["execution_time"] / doc_count
            }
            
            # Verify against thresholds
            threshold = performance_thresholds["indexing"][size_name]["max_time"]
            assert context.stats["execution_time"] < threshold, \
                f"Document indexing for {size_name} set exceeded time threshold: " \
                f"{context.stats['execution_time']:.2f}s > {threshold:.2f}s"
            
            # Clear the index for the next test
            kb_service.clear_index()
        
        # Print comparative results
        print("\n--- Document Indexing Performance Summary ---")
        for size_name in ["small", "medium", "large"]:
            stats = results[size_name]
            print(f"{size_name.capitalize()} set ({stats['doc_count']} docs): "
                  f"{stats['execution_time']:.4f}s total, "
                  f"{stats['avg_time_per_doc']:.4f}s per doc, "
                  f"Memory: {stats['memory_increase_mb']:.2f} MB")
    
    @pytest.mark.skipif(not kb_available, reason="Knowledge base service not available")
    def test_search_performance(self, performance_context, 
                              performance_thresholds, temp_storage):
        """Test the performance of knowledge base search operations."""
        # Initialize services
        storage_service_path = os.path.join(temp_storage, "kb_search_test")
        os.makedirs(storage_service_path, exist_ok=True)
        
        kb_service = KnowledgeBaseService(storage_dir=storage_service_path)
        
        # Generate and index a medium-sized document set (100 docs)
        documents = self._generate_test_documents(100)
        for doc in documents:
            kb_service.add_document(doc)
        
        # Test different query complexities
        query_types = [
            ("simple", "communication relationship"),
            ("medium", "effective communication strategies in relationships"),
            ("complex", "What are the most effective communication strategies for improving relationship dynamics when facing emotional challenges?")
        ]
        
        results = {}
        
        for query_type, query in query_types:
            # Perform search with timing
            with performance_context(f"Knowledge Base Search ({query_type})") as context:
                search_results = kb_service.search(query, limit=10)
            
            # Store the results
            results[query_type] = {
                "execution_time": context.stats["execution_time"],
                "memory_increase_mb": context.stats["memory_increase_mb"],
                "result_count": len(search_results),
                "query_length": len(query)
            }
            
            # Verify against thresholds
            threshold = performance_thresholds["search"][query_type]["max_time"]
            assert context.stats["execution_time"] < threshold, \
                f"Search with {query_type} query exceeded time threshold: " \
                f"{context.stats['execution_time']:.2f}s > {threshold:.2f}s"
        
        # Print comparative results
        print("\n--- Search Performance Summary ---")
        for query_type in ["simple", "medium", "complex"]:
            stats = results[query_type]
            print(f"{query_type.capitalize()} query ({stats['query_length']} chars): "
                  f"{stats['execution_time']:.4f}s, "
                  f"Results: {stats['result_count']}, "
                  f"Memory: {stats['memory_increase_mb']:.2f} MB")
    
    def _generate_test_documents(self, count):
        """Generate a set of test documents for performance testing."""
        topics = [
            "communication", "relationship dynamics", "emotional intelligence",
            "conflict resolution", "active listening", "expressing needs",
            "setting boundaries", "quality time", "love languages",
            "trust building", "vulnerability", "shared experiences"
        ]
        
        documents = []
        
        for i in range(count):
            # Select 1-3 random topics
            doc_topics = random.sample(topics, k=random.randint(1, 3))
            
            # Generate a unique document
            document = {
                "id": str(uuid.uuid4()),
                "title": f"Document on {', '.join(doc_topics)}",
                "content": self._generate_content_for_topics(doc_topics),
                "metadata": {
                    "author": f"Test Author {i % 10 + 1}",
                    "created_date": datetime.now().isoformat(),
                    "topics": doc_topics,
                    "importance": random.randint(1, 5)
                }
            }
            
            documents.append(document)
        
        return documents
    
    def _generate_content_for_topics(self, topics):
        """Generate content paragraphs for the given topics."""
        paragraphs = []
        
        topic_content = {
            "communication": [
                "Effective communication is the cornerstone of any healthy relationship. It involves not just speaking clearly, but also listening actively and with empathy.",
                "When partners can communicate openly and honestly, they build a foundation of understanding and trust that can weather many challenges.",
                "Barriers to communication include fear, defensiveness, and assumptions about the other person's intentions or meanings."
            ],
            "relationship dynamics": [
                "Every relationship has its own unique dynamic, shaped by the personalities, histories, and needs of the individuals involved.",
                "Healthy dynamics include balance of power, mutual respect, and room for both togetherness and individual growth.",
                "Relationship dynamics often evolve over time as both partners grow and change, requiring ongoing attention and adjustment."
            ],
            "emotional intelligence": [
                "Emotional intelligence in relationships involves recognizing, understanding, and managing both your own emotions and your response to your partner's emotions.",
                "Partners with high emotional intelligence can navigate conflicts with less reactivity and more understanding.",
                "Building emotional intelligence requires self-awareness, empathy, and a willingness to examine one's own patterns and triggers."
            ],
            "conflict resolution": [
                "Conflict is inevitable in any relationship, but how couples handle conflict can determine whether it strengthens or weakens their bond.",
                "Effective conflict resolution involves addressing issues directly but respectfully, focusing on solutions rather than blame.",
                "Taking breaks when emotions run high, validating each other's perspectives, and looking for win-win solutions are all healthy conflict strategies."
            ],
            "active listening": [
                "Active listening means fully focusing on what your partner is saying rather than formulating your response or making assumptions.",
                "Techniques include maintaining eye contact, reflecting back what you've heard, and asking clarifying questions.",
                "When partners feel truly heard, they're more likely to open up and share vulnerably, deepening the connection."
            ],
            "expressing needs": [
                "Clearly expressing one's needs is essential in relationships, as partners cannot meet needs they don't know exist.",
                "Using 'I' statements rather than accusations helps partners hear requests without becoming defensive.",
                "Negotiating needs involves recognizing that both partners' needs matter and finding creative ways to honor both."
            ],
            "setting boundaries": [
                "Healthy boundaries protect individuals while allowing for intimacy and connection in the relationship.",
                "Setting boundaries involves clearly communicating one's limits and expectations, and enforcing them consistently.",
                "Respecting a partner's boundaries demonstrates care and builds trust, even when those boundaries limit what we want."
            ],
            "quality time": [
                "Quality time involves giving a partner one's full, undivided attention in a way that builds connection and shared experiences.",
                "Different people may experience quality time differently, from deep conversations to shared activities or simply being together.",
                "Making quality time a priority, even during busy periods, helps maintain connection and prevent drift in the relationship."
            ],
            "love languages": [
                "The concept of love languages recognizes that people give and receive love differently, through words, touch, gifts, service, or time.",
                "Understanding a partner's primary love language helps ensure they feel loved in the way that's most meaningful to them.",
                "Couples may need to 'translate' their natural way of expressing love into their partner's preferred language."
            ],
            "trust building": [
                "Trust is built through consistency, reliability, and honoring commitments both large and small.",
                "Transparency, vulnerability, and admitting mistakes all contribute to an atmosphere of trust in relationships.",
                "Once broken, trust can be rebuilt, but it requires consistent effort, patience, and understanding from both partners."
            ],
            "vulnerability": [
                "Vulnerability—sharing one's true self, including fears, weaknesses, and desires—creates deep intimacy in relationships.",
                "Being vulnerable requires courage and safety, knowing that one's partner will respond with care rather than judgment.",
                "Partners can create safety for vulnerability by responding with empathy, avoiding criticism, and sharing their own vulnerable truths."
            ],
            "shared experiences": [
                "Shared experiences create memories and bonds that strengthen relationships over time.",
                "Both everyday moments and special occasions contribute to a couple's shared history and sense of 'us'.",
                "Trying new things together can add excitement and fresh energy to long-term relationships."
            ]
        }
        
        # Add 2-3 paragraphs for each topic
        for topic in topics:
            topic_paragraphs = topic_content.get(topic, [])
            if topic_paragraphs:
                # Add all paragraphs for smaller topics, or a selection for larger ones
                if len(topic_paragraphs) <= 2 or random.random() < 0.7:
                    paragraphs.extend(topic_paragraphs)
                else:
                    # Select a random subset
                    selected = random.sample(topic_paragraphs, k=random.randint(1, len(topic_paragraphs)))
                    paragraphs.extend(selected)
        
        # Shuffle paragraphs for more natural document flow
        random.shuffle(paragraphs)
        
        # Add an introduction and conclusion
        introduction = f"This document explores {', '.join(topics)} and their impact on relationships."
        conclusion = "Understanding these principles can significantly improve relationship quality and satisfaction."
        
        all_content = [introduction] + paragraphs + [conclusion]
        
        return "\n\n".join(all_content)


@pytest.fixture
def performance_thresholds():
    """Define performance thresholds for benchmark tests."""
    return {
        "analysis": {
            "sentiment": {
                "small": {"max_time": 1.0},    # 1 second
                "medium": {"max_time": 3.0},   # 3 seconds
                "large": {"max_time": 10.0}    # 10 seconds
            },
            "keywords": {
                "small": {"max_time": 0.5},    # 0.5 seconds
                "medium": {"max_time": 2.0},   # 2 seconds
                "large": {"max_time": 8.0}     # 8 seconds
            }
        },
        "indexing": {
            "small": {"max_time": 5.0},      # 5 seconds for 10 docs
            "medium": {"max_time": 20.0},    # 20 seconds for 50 docs
            "large": {"max_time": 60.0}      # 60 seconds for 200 docs
        },
        "search": {
            "simple": {"max_time": 0.5},     # 0.5 seconds
            "medium": {"max_time": 1.0},     # 1 second
            "complex": {"max_time": 2.0}     # 2 seconds
        },
        "file_processing": {
            "small": {"max_time": 0.5},      # 0.5 seconds for small files
            "medium": {"max_time": 2.0},     # 2 seconds for medium files
            "large": {"max_time": 10.0}      # 10 seconds for large files
        }
    }
