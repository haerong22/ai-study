import Markdown from "react-markdown";
import { FiArrowDown, FiSend } from "react-icons/fi";
import type { Message } from "../Models";
import "./style.css";
import { sideBarWidth } from "../Constants";
import { useEffect, useRef, useState } from "react";
import api from "../Api";

interface ChatSideBarProps {
  isOpened: boolean;
}

function ChatSideBar({ isOpened }: ChatSideBarProps) {
  const [prompt, setPrompt] = useState("");
  const [isFetching, setIsFetching] = useState(false);
  const buttonDisabled = !prompt || isFetching;
  const [messages, setMessages] = useState<Message[]>([]);
  const [showScrollDownButton, setShowScrollDownButton] = useState(false);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  const handleSendMessage = async () => {
    const myMessage: Message = {
      role: "user",
      message: prompt,
    };

    setMessages((prev) => [...prev, myMessage]);
    setPrompt("");
    setIsFetching(true);

    try {
      const message = await api.sendMessage({ message: prompt });
      const aiMessage: Message = {
        role: "model",
        message: message.message,
      };
      setMessages((prev) => [...prev, aiMessage]);
    } catch (error) {
      console.error(error);
    } finally {
      setIsFetching(false);
    }
  };

  const scrollContainerToBottom = () => {
    const scrollContainer = scrollContainerRef.current;
    if (!scrollContainer) return;

    scrollContainer.scrollTo({
      top: scrollContainer.scrollHeight,
    });
  };

  useEffect(() => {
    scrollContainerToBottom();
  }, [messages]);

  return (
    <div
      className="chat-side-bar bg-blur-24"
      style={{
        right: isOpened ? 0 : -sideBarWidth,
        width: sideBarWidth,
      }}
    >
      <div className="title">Chat</div>
      <div
        className="content"
        ref={scrollContainerRef}
        onScroll={(event) => {
          const element = event.target as HTMLDivElement;
          const showScrollDown =
            element.scrollHeight - element.scrollTop >
            element.offsetHeight + 100;
          setShowScrollDownButton(showScrollDown);
        }}
      >
        {messages.map((message, index) => (
          <MessageComp key={index} message={message} />
        ))}
      </div>
      {showScrollDownButton && (
        <button
          className="scroll-down-button"
          onClick={scrollContainerToBottom}
        >
          <FiArrowDown size={24} color="rgba(255, 255, 255, 0.7)" />
        </button>
      )}
      <div className="input-wrapper">
        <input
          value={prompt}
          onChange={(event) => setPrompt(event.target.value)}
          placeholder="내용을 입력하세요"
        />
        <FiSend
          size={32}
          color={buttonDisabled ? "#868181ff" : "#db1f1fff"}
          onClick={() => {
            if (buttonDisabled) return;
            handleSendMessage();
          }}
        />
      </div>
    </div>
  );
}

interface MessageCompProp {
  message: Message;
}

function MessageComp({ message }: MessageCompProp) {
  const isUser = message.role === "user";

  return (
    <div
      className="message"
      style={{
        background: isUser ? `rgba(255, 255, 255, 0.07)` : undefined,
        marginLeft: isUser ? 64 : undefined,
        marginRight: isUser ? 16 : undefined,
        borderRadius: isUser ? `8px 0 8px 8px` : undefined,
      }}
    >
      <Markdown>{message.message}</Markdown>
      <div className="created-at">오후 7:44</div>
    </div>
  );
}

export default ChatSideBar;
