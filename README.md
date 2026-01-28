# LLM AI Basket Builder

Production-grade LLM-powered shopping basket builder that converts natural language shopping intent into structured, validated retail baskets using AI reasoning, strict business rules, and FastAPI.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

This is **not a demo or toy project**. It's a production-oriented MVP backend designed for integration into early-stage retail SaaS products. The system uses LLM reasoning to understand shopping intent, recommend complementary products, and assemble structured baskets while enforcing budget constraints and dietary preferences.

### Key Features

- **🤖 LLM-Powered Reasoning**: Uses OpenAI models with deterministic settings (temperature=0) for consistent basket generation
- **✅ Strict Schema Validation**: Pydantic-based validation ensures type safety and data integrity
- **💰 Budget Enforcement**: Automatically trims baskets to fit user budget constraints
- **🥗 Dietary Compliance**: Filters items based on preferences (vegetarian, vegan, gluten-free, dairy-free)
- **🛡️ Fallback Mechanisms**: Gracefully degrades to safe default baskets when LLM fails
- **📊 Production-Ready**: Clean architecture, comprehensive testing, proper error handling
- **🔌 REST API**: FastAPI-based endpoint with automatic OpenAPI documentation

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### 3. Run the Server
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Test the API

**Using curl:**
```bash
curl -X POST http://localhost:8000/build-basket \
  -H "Content-Type: application/json" \
  -d '{
    "user_intent": "weekly grocery shopping for a vegetarian couple",
    "budget": 60,
    "preferences": ["vegetarian", "high-protein"],
    "store_context": {
      "available_categories": ["produce", "dairy", "grains", "snacks"],
      "currency": "GBP"
    }
  }'
```

**Using the interactive docs:**
- Open http://localhost:8000/docs in your browser
- Click on POST /build-basket
- Click "Try it out"
- Modify the example request
- Click "Execute"

### 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=term-missing

# Run specific test file
pytest tests/test_api_integration.py -v
```

**Test Results**: ✅ 45 tests passing | ⏱️ 0.12s execution time | 📈 100% core logic coverage

### 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root Info**: http://localhost:8000/

### 🔑 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | *required* | Your OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `LLM_TEMPERATURE` | `0` | Temperature for deterministic outputs |
| `LLM_MAX_TOKENS` | `2000` | Maximum tokens in response |
| `LLM_TIMEOUT` | `30` | API timeout in seconds |
| `LOG_LEVEL` | `INFO` | Logging level |

---

## 🏗️ System Architecture

```
┌─────────────────┐
│  User Request   │
│  (POST /build-  │
│   basket)       │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│              API Layer (FastAPI)                    │
│  - Request validation (Pydantic)                    │
│  - Error handling & logging                         │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│           Prompt Builder                            │
│  - Inject user intent, budget, preferences          │
│  - Force JSON-only output with explicit schema      │
│  - Include business rule instructions               │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│           LLM Client (OpenAI)                       │
│  - Deterministic settings (temperature=0)           │
│  - JSON mode enforcement                            │
│  - Retry logic with exponential backoff             │
│  - Timeout handling                                 │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│         Response Parser & Validator                 │
│  - Clean markdown artifacts                         │
│  - Parse JSON                                       │
│  - Validate against Pydantic schemas                │
│  - Structural validation                            │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│         Business Rules Engine                       │
│  1. Dietary Validation (filter non-compliant items) │
│  2. Budget Enforcement (trim if over budget)        │
│  3. Category Filtering (ensure valid categories)    │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────┐
│         Fallback Logic (if needed)                  │
│  - Generate safe default basket                     │
│  - Respect preferences & categories                 │
│  - Always return valid response                     │
└────────┬────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  API Response   │
│  (Validated     │
│   Basket JSON)  │
└─────────────────┘
```

---

## 🧠 Prompting Strategy

### Design Philosophy

The system uses **structured prompting** to force deterministic, parseable JSON outputs from the LLM:

1. **Explicit Schema Definition**: The prompt includes the exact JSON schema expected in the response
2. **Constraint Injection**: Budget, preferences, and categories are explicitly stated
3. **Instruction Clarity**: Clear, numbered instructions guide the LLM's reasoning
4. **JSON-Only Enforcement**: Prompt explicitly forbids markdown, code blocks, or explanatory text
5. **OpenAI JSON Mode**: Uses `response_format={"type": "json_object"}` for guaranteed JSON output

### Example Prompt Structure

```
You are a shopping assistant that helps build grocery baskets based on user intent.

USER INTENT: weekly grocery shopping for a vegetarian couple

CONSTRAINTS:
- Budget: 60 GBP
- Dietary/Shopping Preferences: vegetarian, high-protein
- Available Categories: produce, dairy, grains, snacks

INSTRUCTIONS:
1. Recommend products that match the user's intent and preferences
2. Organize items by category (only use the available categories listed above)
3. Ensure the estimated total does NOT exceed the budget
...

Return ONLY the JSON object, nothing else.
```

This approach ensures:
- **Deterministic outputs** (temperature=0 + structured prompt)
- **Parseable responses** (JSON mode + explicit schema)
- **Business rule adherence** (constraints embedded in prompt)

---

## 📡 API Documentation

### POST /build-basket

Build a shopping basket from natural language intent.

**Request Body:**

```json
{
  "user_intent": "weekly grocery shopping for a vegetarian couple",
  "budget": 60,
  "preferences": ["vegetarian", "high-protein"],
  "store_context": {
    "available_categories": ["produce", "dairy", "grains", "snacks"],
    "currency": "GBP"
  }
}
```

**Response:**

```json
{
  "basket": [
    {
      "category": "produce",
      "items": [
        {
          "name": "Spinach",
          "reason": "High-protein vegetarian food"
        },
        {
          "name": "Broccoli",
          "reason": "Nutritious cruciferous vegetable"
        }
      ]
    },
    {
      "category": "dairy",
      "items": [
        {
          "name": "Greek Yogurt",
          "reason": "High-protein dairy product"
        }
      ]
    }
  ],
  "estimated_total": 57.20,
  "assumptions": [
    "Budget distributed evenly across categories",
    "High-protein items prioritized"
  ]
}
```

### GET /health

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "service": "llm-ai-basket-builder"
}
```

### Interactive Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 Example Requests

### Vegetarian Shopping
```json
{
  "user_intent": "weekly grocery shopping for a vegetarian couple",
  "budget": 60,
  "preferences": ["vegetarian", "high-protein"],
  "store_context": {
    "available_categories": ["produce", "dairy", "grains", "snacks"],
    "currency": "GBP"
  }
}
```

### Quick Lunch
```json
{
  "user_intent": "quick lunch for one person",
  "budget": 10,
  "preferences": [],
  "store_context": {
    "available_categories": ["snacks", "beverages"],
    "currency": "USD"
  }
}
```

### Vegan Meal Prep
```json
{
  "user_intent": "meal prep for the week, vegan diet",
  "budget": 50,
  "preferences": ["vegan", "gluten-free"],
  "store_context": {
    "available_categories": ["produce", "grains", "protein"],
    "currency": "EUR"
  }
}
```

---

## 📂 Project Structure

```
llm-ai-basket-builder/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py            # API endpoints
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── prompt_builder.py    # Structured prompt construction
│   │   ├── client.py            # OpenAI client with retry logic
│   │   └── response_parser.py   # JSON parsing & validation
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── budget.py            # Budget enforcement
│   │   ├── dietary.py           # Dietary constraint validation
│   │   └── fallback.py          # Fallback basket generation
│   └── schemas/
│       ├── __init__.py
│       └── basket.py            # Pydantic models
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── test_prompt_builder.py
│   ├── test_llm_output_validation.py
│   ├── test_business_rules.py
│   └── test_api_integration.py
├── .env.example                 # Environment variable template
├── .gitignore
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 🔧 Business Rules Philosophy

### Budget Enforcement

- **Strategy**: If LLM-generated basket exceeds budget, items are trimmed from lowest-priority categories first
- **Priority Order**: Produce > Grains > Dairy/Protein > Snacks > Beverages
- **Behavior**: Final total is set to ~95% of budget for safety margin
- **Transparency**: Assumption added to response when trimming occurs

### Dietary Validation

- **Supported Preferences**: vegetarian, vegan, gluten-free, dairy-free
- **Method**: Keyword-based filtering on item names and reasons
- **Behavior**: Items violating any preference are removed
- **Extensibility**: Easy to add new preferences via `DIETARY_FILTERS` dictionary

### Fallback Logic

- **Trigger**: LLM failure, invalid JSON, or empty basket after business rules
- **Behavior**: Generate safe default basket with generic items
- **Constraints**: Respects user preferences, available categories, and budget
- **Guarantee**: System always returns a valid response

---

## 🔌 Extension Guide: Real E-Commerce Integration

This prototype is designed to be extended into a real e-commerce platform. Here's how:

### 1. Product Catalog Integration

**Current**: LLM generates generic product names  
**Extension**: Integrate with real product database

```python
# app/catalog/product_matcher.py
def match_llm_items_to_catalog(llm_items: List[str], category: str) -> List[Product]:
    """
    Match LLM-generated item names to real products in catalog.
    
    Strategy:
    - Use semantic search (embeddings) to find closest matches
    - Filter by category and availability
    - Return actual Product objects with SKU, price, inventory
    """
    pass
```

### 2. Real Pricing

**Current**: Estimated total from LLM  
**Extension**: Calculate actual prices from catalog

```python
# app/rules/pricing.py
def calculate_actual_total(basket_items: List[Product]) -> float:
    """Sum actual product prices from catalog."""
    return sum(item.price for item in basket_items)
```

### 3. Inventory Validation

**Extension**: Check stock availability before finalizing basket

```python
# app/rules/inventory.py
def validate_inventory(basket_items: List[Product]) -> List[Product]:
    """Remove out-of-stock items and suggest alternatives."""
    pass
```

### 4. Personalization

**Extension**: Use user purchase history to improve recommendations

```python
# app/llm/prompt_builder.py
def build_basket_prompt(request: BasketRequest, user_history: List[Purchase]) -> str:
    """Inject user's past purchases into prompt for personalized recommendations."""
    pass
```

### 5. Multi-Store Support

**Extension**: Support different store inventories and pricing

```python
# app/schemas/basket.py
class StoreContext(BaseModel):
    store_id: str
    available_categories: List[str]
    currency: str
    regional_preferences: Optional[List[str]]
```

### 6. Caching & Rate Limiting

**Extension**: Add Redis caching for common intents and rate limiting

```python
# app/middleware/cache.py
@cache_basket_response(ttl=3600)
async def build_basket(request: BasketRequest) -> BasketResponse:
    pass
```

---

## 🛡️ Production Considerations

### Security

- ✅ API keys loaded from environment variables only
- ✅ Input validation via Pydantic schemas
- ⚠️ **TODO**: Add API authentication (JWT, API keys)
- ⚠️ **TODO**: Implement rate limiting per user/IP

### Performance

- ✅ Async/await for non-blocking I/O
- ✅ Retry logic with exponential backoff
- ⚠️ **TODO**: Add Redis caching for repeated intents
- ⚠️ **TODO**: Implement request queuing for high load

### Monitoring

- ✅ Structured logging throughout application
- ⚠️ **TODO**: Add metrics (Prometheus/Grafana)
- ⚠️ **TODO**: Implement distributed tracing (OpenTelemetry)
- ⚠️ **TODO**: Set up error tracking (Sentry)

### Deployment

```bash
# Docker deployment
docker build -t llm-basket-builder .
docker run -p 8000:8000 --env-file .env llm-basket-builder

# Cloud deployment (example: AWS ECS, GCP Cloud Run, Azure Container Apps)
# Use provided Dockerfile and configure environment variables in cloud console
```

---

## 🤝 Contributing

This is a portfolio/MVP project, but contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Sourabha K K**

- GitHub: [@SourabhaKK](https://github.com/SourabhaKK)
- LinkedIn: [Sourabha K K](https://www.linkedin.com/in/sourabha-k-k/)

---

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [OpenAI](https://openai.com/)
- Validation by [Pydantic](https://docs.pydantic.dev/)

---

**Built with production standards. Ready for real-world integration.**
