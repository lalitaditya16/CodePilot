"""Sample prompts for testing the code generator."""

# Simple algorithm implementations
ALGORITHM_PROMPTS = [
    "Create a function to calculate the factorial of a number",
    "Implement binary search for a sorted array",
    "Write a function to find the greatest common divisor of two numbers",
    "Create a function to check if a number is prime",
    "Implement quicksort algorithm",
    "Write a function to reverse a string",
    "Create a function to find the longest common subsequence",
    "Implement a function to detect cycles in a linked list"
]

# Data structure implementations
DATA_STRUCTURE_PROMPTS = [
    "Implement a stack data structure with push, pop, and peek operations",
    "Create a queue implementation using two stacks",
    "Write a binary tree class with insert, search, and traversal methods",
    "Implement a hash table with collision handling",
    "Create a linked list class with insert, delete, and search operations",
    "Implement a priority queue using a heap",
    "Write a graph class with BFS and DFS traversal methods",
    "Create a trie data structure for string storage and search"
]

# Mathematical functions
MATH_PROMPTS = [
    "Create a function to calculate compound interest",
    "Implement Newton's method for finding square roots",
    "Write a function to generate Pascal's triangle",
    "Create a function to solve quadratic equations",
    "Implement matrix multiplication",
    "Write a function to calculate combinations and permutations",
    "Create a function to find the area of various geometric shapes",
    "Implement numerical integration using the trapezoidal rule"
]

# String processing
STRING_PROMPTS = [
    "Create a function to check if a string is a palindrome",
    "Implement a word count function that handles punctuation",
    "Write a function to find all anagrams of a word",
    "Create a function to validate email addresses using regex",
    "Implement a simple text encryption/decryption function",
    "Write a function to remove duplicate characters from a string",
    "Create a function to find the longest palindromic substring",
    "Implement a basic spell checker"
]

# File and data processing
FILE_PROCESSING_PROMPTS = [
    "Create a function to read and parse CSV files",
    "Write a function to count lines, words, and characters in a text file",
    "Implement a log file analyzer that extracts error messages",
    "Create a function to merge multiple text files",
    "Write a function to find and replace text in files",
    "Implement a basic file backup system",
    "Create a function to extract metadata from image files",
    "Write a function to compress and decompress text using basic algorithms"
]

# Web and API related
WEB_PROMPTS = [
    "Create a function to make HTTP requests and handle responses",
    "Write a function to parse JSON data from an API",
    "Implement a simple URL validator",
    "Create a function to scrape basic information from web pages",
    "Write a function to handle rate limiting for API calls",
    "Implement a basic authentication system",
    "Create a function to generate and validate JWT tokens",
    "Write a function to interact with a REST API"
]

# Complex algorithms
COMPLEX_PROMPTS = [
    "Implement Dijkstra's shortest path algorithm",
    "Create a function for K-means clustering",
    "Write an implementation of the A* pathfinding algorithm",
    "Implement a basic decision tree classifier",
    "Create a function for linear regression with gradient descent",
    "Write a function to solve the traveling salesman problem",
    "Implement a basic neural network with backpropagation",
    "Create a function for image edge detection using convolution"
]

# Utility functions
UTILITY_PROMPTS = [
    "Create a function to generate random passwords with specific criteria",
    "Write a function to convert between different number bases",
    "Implement a date/time utility with timezone handling",
    "Create a function to validate and format phone numbers",
    "Write a function to calculate file checksums",
    "Implement a basic caching mechanism with expiration",
    "Create a function to format numbers as currency",
    "Write a function to generate QR codes"
]

# All prompts combined
ALL_PROMPTS = (
    ALGORITHM_PROMPTS + 
    DATA_STRUCTURE_PROMPTS + 
    MATH_PROMPTS + 
    STRING_PROMPTS + 
    FILE_PROCESSING_PROMPTS + 
    WEB_PROMPTS + 
    COMPLEX_PROMPTS + 
    UTILITY_PROMPTS
)

# Prompts with specific requirements for testing advanced features
ADVANCED_PROMPTS = [
    {
        "description": "Create a binary search function",
        "function_name": "binary_search",
        "parameters": ["arr: List[int]", "target: int"],
        "return_type": "int",
        "additional_requirements": "Return -1 if target not found, include proper error handling for empty arrays"
    },
    {
        "description": "Implement a recursive factorial function",
        "function_name": "factorial",
        "parameters": ["n: int"],
        "return_type": "int",
        "additional_requirements": "Include input validation for negative numbers, optimize for large numbers"
    },
    {
        "description": "Create a text processing function",
        "function_name": "process_text",
        "parameters": ["text: str", "operation: str"],
        "return_type": "str",
        "additional_requirements": "Support operations: 'uppercase', 'lowercase', 'reverse', 'word_count'"
    },
    {
        "description": "Implement a simple cache system",
        "function_name": "create_cache",
        "parameters": ["max_size: int"],
        "return_type": "Dict[str, Any]",
        "additional_requirements": "Use LRU eviction policy, thread-safe operations, include cache statistics"
    }
]


def get_random_prompt():
    """Get a random prompt for testing."""
    import random
    return random.choice(ALL_PROMPTS)


def get_prompts_by_category(category: str):
    """Get prompts from a specific category."""
    categories = {
        'algorithms': ALGORITHM_PROMPTS,
        'data_structures': DATA_STRUCTURE_PROMPTS,
        'math': MATH_PROMPTS,
        'strings': STRING_PROMPTS,
        'files': FILE_PROCESSING_PROMPTS,
        'web': WEB_PROMPTS,
        'complex': COMPLEX_PROMPTS,
        'utilities': UTILITY_PROMPTS,
        'advanced': ADVANCED_PROMPTS
    }
    return categories.get(category.lower(), [])


def get_test_batch(count: int = 5):
    """Get a batch of prompts for testing."""
    import random
    return random.sample(ALL_PROMPTS, min(count, len(ALL_PROMPTS)))


if __name__ == "__main__":
    print("Sample Prompts for Code Generation Testing")
    print("=" * 50)
    
    print(f"\nTotal prompts available: {len(ALL_PROMPTS)}")
    
    print("\nCategories:")
    categories = {
        'Algorithms': len(ALGORITHM_PROMPTS),
        'Data Structures': len(DATA_STRUCTURE_PROMPTS),
        'Mathematics': len(MATH_PROMPTS),
        'String Processing': len(STRING_PROMPTS),
        'File Processing': len(FILE_PROCESSING_PROMPTS),
        'Web/API': len(WEB_PROMPTS),
        'Complex Algorithms': len(COMPLEX_PROMPTS),
        'Utilities': len(UTILITY_PROMPTS),
        'Advanced (structured)': len(ADVANCED_PROMPTS)
    }
    
    for category, count in categories.items():
        print(f"  {category}: {count} prompts")
    
    print("\nRandom sample prompts:")
    for i, prompt in enumerate(get_test_batch(3), 1):
        print(f"  {i}. {prompt}")
    
    print("\nAdvanced structured prompt example:")
    advanced_example = ADVANCED_PROMPTS[0]
    print(f"  Description: {advanced_example['description']}")
    print(f"  Function: {advanced_example['function_name']}")
    print(f"  Parameters: {advanced_example['parameters']}")
    print(f"  Return Type: {advanced_example['return_type']}")
    print(f"  Requirements: {advanced_example['additional_requirements']}")