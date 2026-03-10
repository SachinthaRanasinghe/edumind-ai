import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function AITutor() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hello! I\'m your AI tutor. Ask me anything about your courses!' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const { aiAPI } = await import('../services/api');
      const data = await aiAPI.chatWithTutor(userMessage, null, 'general');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.response || 'I\'m here to help! Could you rephrase your question?' 
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      const fallbackResponse = getFallbackResponse(userMessage);
      setMessages(prev => [...prev, { role: 'assistant', content: fallbackResponse }]);
    } finally {
      setLoading(false);
    }
  };

  const getFallbackResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('variable')) {
      return 'A variable is like a labeled container that stores data in your program. For example, in Python: `name = "Alice"` creates a variable called "name" that stores the text "Alice".';
    } else if (lowerMessage.includes('loop')) {
      return 'Loops help you repeat code multiple times. In Python, a `for` loop can iterate through items: `for i in range(5):` will run 5 times. A `while` loop runs as long as a condition is true.';
    } else if (lowerMessage.includes('function')) {
      return 'A function is a reusable block of code that performs a specific task. You define it with `def function_name():` in Python. Functions help organize your code and make it easier to maintain.';
    } else if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
      return 'I\'m here to help you learn! You can ask me about programming concepts, get explanations of topics, or request help with specific problems. Try asking: "What is a variable?" or "How do loops work?"';
    } else {
      return 'That\'s a great question! While I\'m working on understanding it better, I can help you with topics like variables, loops, functions, data types, and more. What would you like to learn about?';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate(-1)}
              className="text-blue-600 hover:text-blue-700 font-medium"
            >
              ← Back
            </button>
            <div>
              <h1 className="text-2xl font-bold">🤖 AI Tutor</h1>
              <p className="text-sm text-gray-600">Your 24/7 learning assistant</p>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="bg-white rounded-lg shadow h-[600px] flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 rounded-lg px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t p-4">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about your courses..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                disabled={loading}
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
              >
                Send
              </button>
            </div>
            
            {/* Quick Questions */}
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                onClick={() => setInput('What is a variable?')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
              >
                What is a variable?
              </button>
              <button
                onClick={() => setInput('Explain loops')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
              >
                Explain loops
              </button>
              <button
                onClick={() => setInput('How do functions work?')}
                className="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200"
              >
                How do functions work?
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
