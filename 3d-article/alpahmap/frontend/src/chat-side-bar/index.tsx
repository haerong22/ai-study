import Markdown from "react-markdown";
import { FiSend } from "react-icons/fi";
import type { Message } from "../Models";
import "./style.css";
import { sideBarWidth } from "../Constants";
import { useState } from "react";

const dummyMessages: Message[] = [
  {
    message: "ㅎㅇ",
    role: "user",
  },
  {
    message: "네 안녕하세요. 무슨 일을 도와드릴까요",
    role: "model",
  },
];

interface ChatSideBarProps {
  isOpened: boolean;
}

function ChatSideBar({ isOpened }: ChatSideBarProps) {
  const [prompt, setPrompt] = useState("");
  const [isFetching, setIsFetching] = useState(false);
  const buttonDisabled = !prompt || isFetching;

  const handleSendMessage = () => {};

  return (
    <div
      className="chat-side-bar bg-blur-24"
      style={{
        right: isOpened ? 0 : -sideBarWidth,
        width: sideBarWidth,
      }}
    >
      <div className="title">Chat</div>
      <div className="content">
        {dummyMessages.map((message, index) => (
          <MessageComp key={index} message={message} />
        ))}
      </div>
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
