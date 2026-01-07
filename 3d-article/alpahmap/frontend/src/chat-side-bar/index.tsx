import Markdown from "react-markdown";
import type { Message } from "../Models";
import "./style.css";
import { sideBarWidth } from "../Constants";

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
