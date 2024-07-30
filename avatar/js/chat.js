const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = true;
recognition.interimResults = false;
recognition.lang = "en-US";

function Chat() {
  const [messages, setMessages] = useState([]);
  const chatWindowRef = useRef(null);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(false);
  const [isListening, setIsListening] = useState(false);



  useEffect(() => {
    const handleResult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      console.log("Transcript:", transcript);
      sendInput(transcript);
    };

    recognition.onresult = handleResult;

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      if (event.error === "no-speech" || event.error === "audio-capture") {
        recognition.stop();
        setIsListening(false);
      }
    };

    recognition.onend = () => {
      if (isListening) {
        recognition.start();
      }
    };

    if (isListening) {
      recognition.start();
    } else {
      recognition.stop();
    }

    return () => {
      recognition.removeEventListener("result", handleResult);
      recognition.stop();
    };
  }, [isListening]);

  const sendInput = (input) => {
    const newMessage = { text: input, sender: "user" };
    setMessages((prevMessages) => [
      ...prevMessages,
      newMessage,
      { text: "Generating answer...", sender: "bot" },
    ]);

    const params = new URLSearchParams({
      username: "sonugahatraj5-texas", // or dynamically set based on logged in user
      question: input,
    });

    axios
      .get("http://127.0.0.1:8000/api/get_response/", {
        params,
        timeout: 200000,
      })
      .then((response) => {
        console.log("server response:", response);
        const botReply = response.data.response;
        const audioUrl = response.data.audio; // Get the audio URL from the response
        console.log("Audio URL: ", audioUrl); // Log the audio URL

        const botMessage = { text: botReply, sender: "bot", audio: audioUrl };

        if (isVoiceEnabled) {
          const speech = new SpeechSynthesisUtterance(botReply);
          window.speechSynthesis.speak(speech);
        }

        setMessages((prev) => [
          ...prev.slice(0, -1), // Remove the "Generating answer..." message
          botMessage,
        ]);

        if (audioUrl) {
          const audioElement = document.getElementById("audio-element");
          if (audioElement) {
            audioElement.src = audioUrl;
            audioElement
              .play()
              .catch((error) => console.log("Error playing audio:", error)); // Catch and log any errors
          }
        }
      })
      .catch((error) => {
        console.error("Error fetching data: ", error);
        setMessages((prev) => [
          ...prev.slice(0, -1), // Remove the "Generating answer..." message
          {
            text: "Sorry, I did not get you. Can you please ask it again louder and clearer?",
            sender: "bot",
          },
        ]);
      });
  };

  const handleStartListening = () => {
    setIsListening(true);
  };

  const handleStopListening = () => {
    setIsListening(false);
  };

  return (
    <div className="App">
      
      <main className="chat-main">

        <section className="chat-container">
          <div className="chat-window" ref={chatWindowRef}>
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message-container ${message.sender}`}
              >
                <label className="message-label">
                  {message.sender === "bot" ? "Bot" : "You"}
                </label>
                <div className={`message ${message.sender}`}>
                  {message.text.split("\n").map((line, idx) => (
                    <p key={idx}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
          </div>
          <div className="controls">
            <button
              onClick={isListening ? handleStopListening : handleStartListening}
              className={isListening ? "listening" : ""}
            >
              {isListening && (
                <div className="recording-indicator">
                  <div className="bar"></div>
                  <div className="bar"></div>
                  <div className="bar"></div>
                  <div className="bar"></div>
                  <div className="bar"></div>
                </div>
              )}
              <FiMic />
            </button>
          </div>
        </section>
        <audio id="audio-element" controls style={{ display: "none" }}></audio>
      </main>
    </div>
  );
}

export default Chat;

ReactDOM.render(<Chat />, document.getElementById("root"));