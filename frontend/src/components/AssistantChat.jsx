import { useState } from "react";

function AssistantChat() {
  const [isOpen, setIsOpen] = useState(false);

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Bonjour ! Je suis l'assistant Smart Mobility. Comment puis-je vous aider ?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [sessionId] = useState("web-user-1");

  const sendMessage = async () => {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setMessages((currentMessages) => [
      ...currentMessages,
      {
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setLoading(true);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/assistant/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message,
            session_id: sessionId,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(
          "Erreur lors de la communication avec l'assistant."
        );
      }

      const data = await response.json();

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content: data.response,
        },
      ]);
    } catch (error) {
      console.error(error);

      setMessages((currentMessages) => [
        ...currentMessages,
        {
          role: "assistant",
          content:
            "Je n'arrive pas à contacter l'assistant pour le moment.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      sendMessage();
    }
  };

  return (
    <>
      {!isOpen && (
        <button
          className="assistant-floating-button"
          onClick={() => setIsOpen(true)}
        >
          💬 Assistant
        </button>
      )}

      {isOpen && (
        <div className="assistant-panel">
          <div className="assistant-header">
            <div>
              <strong>Assistant Smart Mobility</strong>
              <span>En ligne</span>
            </div>

            <button
              className="assistant-close"
              onClick={() => setIsOpen(false)}
            >
              ✕
            </button>
          </div>

          <div className="assistant-messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`assistant-message ${message.role}`}
              >
                <p>{message.content}</p>
              </div>
            ))}

            {loading && (
              <div className="assistant-message assistant">
                <p>Recherche en cours...</p>
              </div>
            )}
          </div>

          <div className="assistant-input">
            <input
              type="text"
              value={input}
              placeholder="Posez votre question..."
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={loading}
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
            >
              Envoyer
            </button>
          </div>
        </div>
      )}
    </>
  );
}

export default AssistantChat;