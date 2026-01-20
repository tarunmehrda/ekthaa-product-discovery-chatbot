# Ekthaa - Smart Product Discovery Chatbot

A modern, AI-powered chatbot for discovering local grocery and vegetable products in Hyderabad. Built with FastAPI backend, Groq AI integration, and a clean, responsive frontend.

## 🌟 Features

- **🤖 AI-Powered Search**: Uses Groq's Llama 3.1 model for natural language understanding
- **🛍️ Product Discovery**: Find groceries, vegetables, and compare prices
- **📍 Store Locator**: Discover local stores and their contact information
- **💰 Price Filtering**: Search products within your budget
- **🎯 Smart Suggestions**: Context-aware query suggestions
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **⚡ Real-time Chat**: Instant responses with typing indicators

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key (get one at [console.groq.com](https://console.groq.com))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ekthaa-product-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your Groq API key
   ```

4. **Initialize the database**
   ```bash
   python database/seed.py
   ```

5. **Start the server**
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open the frontend**
   - Navigate to `frontend/index.html` in your browser
   - Or open `http://localhost:8000` for the API health check

## 📁 Project Structure

```
ekthaa-product-chatbot/
├── app.py                 # Main FastAPI application
├── requirements.txt        # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── database/
│   ├── ekthaa.db        # SQLite database
│   └── seed.py          # Database seeding script
├── frontend/
│   ├── index.html        # Main frontend page
│   ├── style.css         # Styling
│   └── script.js        # Frontend JavaScript
├── utils/
│   ├── groq_client.py   # Groq API integration
│   ├── query_parser.py  # Query parsing utilities
│   ├── response_formatter.py # Response formatting
│   └── memory.py        # Conversation memory
└── tests/
    └── test_queries.txt  # Sample test queries
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Database Setup

The project uses SQLite for simplicity. Run the seed script to populate it with sample data:

```bash
python database/seed.py
```

This creates sample products, businesses, and categories for Hyderabad stores.

## 📡 API Endpoints

### Chat Endpoint
- **POST** `/chat`
  - Send messages to the chatbot
  - Request body:
    ```json
    {
      "message": "Show me rice under 150",
      "user_id": "user123",
      "location": {
        "latitude": 17.4485,
        "longitude": 78.3908
      }
    }
    ```

### Suggestions Endpoint
- **GET** `/suggest`
  - Get contextual question suggestions
  - Returns a list of sample queries

### Health Check
- **GET** `/`
  - Check if the API is running

## 🎨 Frontend Features

### User Interface
- **Clean, modern design** with responsive layout
- **Real-time typing indicators** for better UX
- **Message timestamps** and conversation flow
- **Product cards** with detailed information
- **Smart suggestions** with one-click queries
- **Mobile-friendly** responsive design

### Interactive Elements
- **Enter to send** messages
- **Clear chat** functionality
- **Refresh suggestions** button
- **Smooth animations** and transitions
- **Error handling** with user-friendly messages

## 🤖 AI Integration

The chatbot uses Groq's Llama 3.1 8B Instant model for:

- **Intent Extraction**: Understanding user queries
- **Entity Recognition**: Identifying products, prices, categories
- **Contextual Responses**: Generating helpful replies
- **Fallback Handling**: Graceful responses when no results found

### Supported Intents

- `product_search`: Find specific products
- `price_filter`: Search within budget
- `category_search`: Browse by category
- `business_finder`: Locate stores
- `no_result`: Handle empty results

## 📊 Sample Queries

Try these sample queries:

- "Show me rice under 150"
- "Where can I buy vegetables?"
- "Grocery stores near me"
- "Who sells dal?"
- "Products under Rs.50"
- "Do you have apples?"

## 🛠️ Development

### Adding New Products

Edit `database/seed.py` to add new products, businesses, or categories:

```python
# Add a new product
cursor.execute("""
    INSERT INTO products (name, price, unit, category, business_id)
    VALUES (?, ?, ?, ?, ?)
""", ("Product Name", 100, "kg", "Grocery", 1))
```

### Customizing AI Responses

Modify the system prompts in `utils/groq_client.py`:

```python
# Update llm_extract system prompt for better intent recognition
system = """
You are an NLU engine for a product discovery chatbot...
"""
```

### Frontend Customization

- **Styling**: Edit `frontend/style.css` for visual changes
- **Functionality**: Modify `frontend/script.js` for behavior
- **Structure**: Update `frontend/index.html` for layout

## 🔍 Testing

### Test Queries

Use the sample queries in `tests/test_queries.txt` to test various scenarios:

```bash
# Test manually via curl
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Show me rice", "user_id": "test"}'
```

### Frontend Testing

1. Open `frontend/index.html` in your browser
2. Test various query types
3. Verify responsive design on different screen sizes
4. Check error handling with invalid inputs

## 📱 Mobile Support

The frontend is fully responsive and works on:

- **Desktop browsers** (Chrome, Firefox, Safari, Edge)
- **Mobile browsers** (iOS Safari, Chrome Mobile)
- **Tablets** (iPad, Android tablets)

## 🚀 Deployment

### Docker Deployment

1. **Create Dockerfile**:
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 8000
   CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Build and run**:
   ```bash
   docker build -t ekthaa-chatbot .
   docker run -p 8000:8000 ekthaa-chatbot
   ```

### Cloud Deployment

Deploy to platforms like:
- **Heroku** (with PostgreSQL addon)
- **AWS** (Elastic Beanstalk or Lambda)
- **Google Cloud** (Cloud Run)
- **Azure** (App Service)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Groq API Error**
   - Ensure your API key is valid in `.env`
   - Check your Groq API quota

2. **Database Connection Error**
   - Run `python database/seed.py` to initialize
   - Check file permissions for `database/ekthaa.db`

3. **CORS Issues**
   - Ensure backend is running on port 8000
   - Check frontend API URL in `script.js`

4. **Frontend Not Loading**
   - Open `frontend/index.html` directly in browser
   - Check browser console for errors

### Debug Mode

Enable debug logging by modifying `app.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section above
- Review the API documentation

---

**Built with ❤️ using FastAPI, Groq AI, and modern web technologies**